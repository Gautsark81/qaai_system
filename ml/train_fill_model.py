# ml/train_fill_model.py
"""
Train a simple fill-probability model from historical execution logs.

Usage:
    python ml/train_fill_model.py --input data/orders.parquet --out models/fill_model.pkl

If no input exists, the script will create a small synthetic dataset to demonstrate flow.
"""
import argparse
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
import joblib


def featurize(df: pd.DataFrame) -> pd.DataFrame:
    # Basic features: side, qty, price, hour, weekday, historical position, last_price, volatility proxy
    out = pd.DataFrame()
    out["qty"] = df.get("quantity", df.get("qty", 0)).astype(float)
    out["price"] = df.get("price", 0.0).astype(float)
    out["side_buy"] = (df.get("side", "buy") == "buy").astype(int)
    ts = pd.to_datetime(df.get("timestamp", df.get("ts", pd.NaT)))
    out["hour"] = ts.dt.hour.fillna(0).astype(int)
    out["weekday"] = ts.dt.weekday.fillna(0).astype(int)
    out["nav"] = df.get("account_nav", 0.0).astype(float)
    # last price (if present)
    out["last_price"] = (
        df.get("last_price", out["price"]).astype(float).fillna(out["price"])
    )
    # simple derived features
    out["qty_nav_ratio"] = out["qty"] / (out["nav"].replace(0, np.nan)).fillna(1.0)
    # fill outcome: consider 'status' == 'filled' or 'filled' column boolean
    if "status" in df.columns:
        y = (df["status"] == "filled").astype(int)
    elif "filled" in df.columns:
        y = df["filled"].astype(int)
    else:
        # synthetic heuristic: treat price < last_price as more likely to be filled
        y = (out["price"] <= out["last_price"]).astype(int)
    return out.fillna(0.0), y


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"No data at {path}, generating synthetic data (demo mode).")
        n = 2000
        rng = np.random.RandomState(42)
        ts = pd.date_range("2024-01-01", periods=n, freq="T")
        df = pd.DataFrame(
            {
                "timestamp": ts,
                "quantity": rng.randint(1, 100, size=n),
                "price": rng.uniform(10, 200, size=n),
                "side": rng.choice(["buy", "sell"], size=n),
                "account_nav": rng.uniform(10000, 20000, size=n),
            }
        )
        # synthetic fill: higher qty/narrow price have lower fill prob
        df["last_price"] = df["price"] + rng.normal(0, 1, size=n)
        df["status"] = np.where(rng.rand(n) < 0.6, "filled", "open")
        return df
    # try parquet then csv
    if path.suffix in [".parquet", ".pq"]:
        return pd.read_parquet(path)
    else:
        return pd.read_csv(path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/orders.parquet")
    p.add_argument("--out", default="models/fill_model.pkl")
    args = p.parse_args()

    os.makedirs(Path(args.out).parent, exist_ok=True)
    df = load_data(Path(args.input))
    X, y = featurize(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=200, max_depth=10, random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    print("ROC-AUC:", auc)
    preds = model.predict(X_test)
    print(classification_report(y_test, preds))
    joblib.dump({"model": model, "features": list(X.columns)}, args.out)
    print("Model saved to", args.out)


if __name__ == "__main__":
    main()
