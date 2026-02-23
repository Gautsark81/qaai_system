#!/usr/bin/env python3
"""
ml/train_fill_v3.py

Supercharged training with cross-validation and randomized hyperparameter search.

Usage:
    python ml/train_fill_v3.py \
        --input data/orders.parquet \
        --out-model models/fill_model_v3.pkl \
        --out-meta models/fill_model_v3_meta.json \
        --reports reports/

If no input data is found, the script will generate a synthetic dataset for demo.
"""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, Dict
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    RandomizedSearchCV,
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    precision_recall_curve,
    auc,
    classification_report,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------------------
# Data loading + synthetic fallback
# ----------------------------
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.info("No data at %s — generating synthetic demo dataset", path)
        n = 10000
        rng = np.random.RandomState(42)
        ts = pd.date_range("2024-01-01", periods=n, freq="min")
        df = pd.DataFrame(
            {
                "timestamp": ts,
                "symbol": rng.choice(["AAA", "BBB", "CCC", "SYM", "XYZ"], size=n),
                "quantity": rng.randint(1, 500, size=n),
                "price": rng.uniform(5, 500, size=n),
                "side": rng.choice(["buy", "sell"], size=n),
                "account_nav": rng.uniform(10000, 200000, size=n),
            }
        )
        df["last_price"] = df["price"] + rng.normal(0, 2.0, size=n)
        # synthetic fill signal: price closeness to last_price and a symbol effect
        prob = 0.25 + 0.5 * (df["price"] <= df["last_price"])
        # symbol bias
        symbol_bias = df["symbol"].map(
            {"AAA": 0.1, "BBB": -0.05, "CCC": 0.05, "SYM": 0.0, "XYZ": -0.02}
        )
        prob = np.clip(prob + symbol_bias.values, 0.01, 0.99)
        df["status"] = np.where(rng.rand(n) < prob, "filled", "open")
        return df
    if path.suffix in (".parquet", ".pq"):
        return pd.read_parquet(path)
    else:
        return pd.read_csv(path)


# ----------------------------
# feature engineering (same canonical features as v2)
# ----------------------------
def compute_symbol_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "symbol" not in df.columns:
        df["symbol"] = "UNKNOWN"
    df["symbol_fill_rate"] = df.groupby("symbol")["status"].transform(
        lambda s: (s == "filled").rolling(200, min_periods=1).mean()
    )
    df["symbol_avg_qty"] = df.groupby("symbol")["quantity"].transform(
        lambda s: s.rolling(200, min_periods=1).mean()
    )
    if "last_price" in df.columns:
        df["symbol_volatility"] = (
            df.groupby("symbol")["last_price"]
            .transform(lambda s: s.rolling(50, min_periods=1).std())
            .fillna(0)
        )
    else:
        df["symbol_volatility"] = 0.0
    return df


def featurize(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    df["quantity"] = df.get("quantity", df.get("qty", 0)).astype(float)
    df["price"] = df.get("price", 0.0).astype(float)
    df["side_buy"] = (df.get("side", "buy") == "buy").astype(int)
    ts = pd.to_datetime(df.get("timestamp", df.get("ts", pd.NaT)))
    df["hour"] = ts.dt.hour.fillna(0).astype(int)
    df["weekday"] = ts.dt.weekday.fillna(0).astype(int)
    df["account_nav"] = df.get("account_nav", df.get("nav", 0.0)).astype(float)
    df["last_price"] = df.get("last_price", df["price"])
    df["price_diff"] = df["last_price"] - df["price"]
    df["pct_diff"] = df["price_diff"] / df["last_price"].replace(0, np.nan)
    df["pct_diff"] = df["pct_diff"].fillna(0)
    df["is_aggressive_buy"] = (df["price"] >= df["last_price"]).astype(int)
    df["is_aggressive_sell"] = (df["price"] <= df["last_price"]).astype(int)
    df["spread_abs"] = df["price_diff"].abs()
    df["qty_nav_ratio"] = df["quantity"] / df["account_nav"].replace(0, np.nan)
    df["qty_nav_ratio"] = df["qty_nav_ratio"].fillna(0)
    df = compute_symbol_stats(df)
    if "status" in df.columns:
        y = (df["status"] == "filled").astype(int)
    else:
        y = (df["price"] <= df["last_price"]).astype(int)
    feature_cols = [
        "quantity",
        "price",
        "side_buy",
        "hour",
        "weekday",
        "account_nav",
        "last_price",
        "price_diff",
        "pct_diff",
        "is_aggressive_buy",
        "is_aggressive_sell",
        "spread_abs",
        "qty_nav_ratio",
        "symbol_fill_rate",
        "symbol_avg_qty",
        "symbol_volatility",
    ]
    X = df[feature_cols].fillna(0)
    return X, y


# ----------------------------
# Utilities: plotting and save
# ----------------------------
def save_roc_pr(y_true: np.ndarray, y_score: np.ndarray, out_prefix: Path) -> None:
    # ROC
    fpr = None
    tpr = None
    try:
        from sklearn.metrics import roc_curve

        fpr, tpr, _ = roc_curve(y_true, y_score)
        roc_auc = roc_auc_score(y_true, y_score)
        plt.figure()
        plt.plot(fpr, tpr)
        plt.xlabel("FPR")
        plt.ylabel("TPR")
        plt.title(f"ROC curve (AUC={roc_auc:.3f})")
        plt.grid(True)
        out = out_prefix.with_suffix(".roc.png")
        plt.savefig(out)
        plt.close()
    except Exception as e:
        logger.debug("Failed to save ROC: %s", e)

    # PR
    try:
        precision, recall, _ = precision_recall_curve(y_true, y_score)
        pr_auc = auc(recall, precision)
        plt.figure()
        plt.plot(recall, precision)
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title(f"PR curve (AUC={pr_auc:.3f})")
        plt.grid(True)
        out2 = out_prefix.with_suffix(".pr.png")
        plt.savefig(out2)
        plt.close()
    except Exception as e:
        logger.debug("Failed to save PR: %s", e)


# ----------------------------
# Hyperparameter search space
# ----------------------------
def build_search_space() -> Dict[str, list]:
    return {
        "clf__n_estimators": [100, 200, 400, 800],
        "clf__max_depth": [3, 5, 8, 12, None],
        "clf__min_samples_split": [2, 5, 10],
        "clf__min_samples_leaf": [1, 2, 4],
        "clf__max_features": ["sqrt", "log2", None],
    }


# ----------------------------
# Train function
# ----------------------------
def train_and_select(
    X: pd.DataFrame,
    y: pd.Series,
    out_model: Path,
    out_meta: Path,
    reports_dir: Path,
    random_state: int = 42,
):
    # hold-out test split
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    logger.info("Train/test split: %d/%d", len(X_train_full), len(X_test))

    # pipeline: scaler + classifier
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(random_state=random_state, n_jobs=-1)),
        ]
    )

    # cross validation and randomized search
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    param_dist = build_search_space()
    rs = RandomizedSearchCV(
        pipeline,
        param_distributions=param_dist,
        n_iter=40,
        scoring="roc_auc",
        n_jobs=-1,
        cv=cv,
        verbose=2,
        random_state=random_state,
        refit=True,
    )

    logger.info("Starting RandomizedSearchCV...")
    rs.fit(X_train_full, y_train_full)

    logger.info("Best params: %s", rs.best_params_)
    logger.info("Best CV score: %s", rs.best_score_)

    # evaluate on holdout test
    best = rs.best_estimator_
    y_proba = best.predict_proba(X_test)[:, 1]
    test_auc = roc_auc_score(y_test, y_proba)
    logger.info("Test ROC-AUC: %.4f", test_auc)

    # Save ROC/PR plots and classification report
    reports_dir.mkdir(parents=True, exist_ok=True)
    prefix = reports_dir / f"fill_model_v3_{int(time.time())}"
    save_roc_pr(y_test.values, y_proba, prefix)
    preds = best.predict(X_test)
    report = classification_report(y_test, preds, output_dict=True)
    with open(reports_dir / "classification_report.json", "w") as fh:
        json.dump(report, fh, indent=2)

    # Feature importances (if underlying classifier supports it)
    feature_names = X.columns.tolist()
    importances = None
    try:
        clf = best.named_steps["clf"]
        if hasattr(clf, "feature_importances_"):
            importances = clf.feature_importances_.tolist()
            feat_imp = sorted(zip(feature_names, importances), key=lambda x: -x[1])
            with open(reports_dir / "feature_importance.json", "w") as fh:
                json.dump({"feature_importance": feat_imp}, fh, indent=2)
    except Exception as e:
        logger.debug("Could not compute feature importances: %s", e)

    # Save model and metadata
    model_obj = {"model": best, "features": feature_names}
    joblib.dump(model_obj, out_model)

    meta = {
        "model_path": str(out_model),
        "features": feature_names,
        "train_size": int(len(X_train_full)),
        "test_size": int(len(X_test)),
        "cv_best_score": float(rs.best_score_),
        "test_auc": float(test_auc),
        "search_params": rs.best_params_,
        "timestamp": int(time.time()),
    }
    with open(out_meta, "w") as fh:
        json.dump(meta, fh, indent=2)

    logger.info("Saved model to %s and metadata to %s", out_model, out_meta)


# ----------------------------
# CLI
# ----------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/orders.parquet")
    p.add_argument("--out-model", default="models/fill_model_v3.pkl")
    p.add_argument("--out-meta", default="models/fill_model_v3_meta.json")
    p.add_argument("--reports", default="reports")
    p.add_argument("--random-state", type=int, default=42)
    args = p.parse_args()

    input_path = Path(args.input)
    out_model = Path(args.out_model)
    out_meta = Path(args.out_meta)
    reports_dir = Path(args.reports)
    os.makedirs(out_model.parent, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    df = load_data(input_path)
    X, y = featurize(df)

    # small sanity checks
    if len(X) < 100:
        logger.warning(
            "Very small dataset (%d rows). Consider more data for robust models.",
            len(X),
        )

    train_and_select(
        X, y, out_model, out_meta, reports_dir, random_state=args.random_state
    )
    logger.info("Training complete.")


if __name__ == "__main__":
    main()
