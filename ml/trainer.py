# ml/trainer.py
from __future__ import annotations
import os
import sys

# Ensure repo root is on sys.path so module imports work when script executed directly.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import argparse
import pandas as pd
from typing import Tuple, Any, Dict
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import joblib

try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except Exception:
    LGB_AVAILABLE = False

from ml.model_registry import ModelRegistry

def load_examples(path: str) -> pd.DataFrame:
    """
    Load training examples CSV/Parquet. Expect a table with features and 'label' column.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Examples file not found: {path}\nPlease provide a valid path to CSV or Parquet with a 'label' column.")
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path)

def train_model(df: pd.DataFrame, target_col: str = "label") -> Tuple[Any, Dict]:
    X = df.drop(columns=[target_col])
    y = df[target_col]
    strat = y if len(set(y)) > 1 else None
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=strat)

    if LGB_AVAILABLE:
        dtrain = lgb.Dataset(X_train, label=y_train)
        dval = lgb.Dataset(X_val, label=y_val, reference=dtrain)
        params = {
            "objective": "binary",
            "metric": "auc",
            "verbosity": -1,
            "boosting_type": "gbdt",
            "seed": 42,
            "num_threads": 2,
        }
        model = lgb.train(params, dtrain, valid_sets=[dval], num_boost_round=200, early_stopping_rounds=20, verbose_eval=False)
        preds = model.predict(X_val)
    else:
        # fallback: simple sklearn
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_val)[:, 1]

    auc = float(roc_auc_score(y_val, preds)) if len(set(y_val)) > 1 else 0.5
    metadata = {"auc": auc, "n_samples": int(len(df))}
    return model, metadata

def main(example_path: str, model_name: str, registry_dir: str = "ml_models"):
    df = load_examples(example_path)
    model, metadata = train_model(df)
    reg = ModelRegistry(registry_dir)
    meta = reg.save_model(model, model_name, metadata)
    print("Saved model:", meta)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("examples", help="Path to examples CSV or Parquet containing a 'label' column")
    p.add_argument("--name", required=True)
    p.add_argument("--registry", default="ml_models")
    args = p.parse_args()
    main(args.examples, args.name, args.registry)
