"""
Meta-model training pipeline.

Features:
- Builds dataset from daily rolling features + forward targets
- Purged time-series CV / LightGBM training (binary target)
- Model save & CV reporting

This file is hardened for missing feature files and small datasets.

Note: this script expects the feature-building step to have been run and
a features file available at data/meta/features_rolling_20.parquet or the
script will attempt to compute features from trade logs.
"""

from __future__ import annotations
import argparse
import logging
from pathlib import Path
import pickle

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Local imports (feature_engine is the module above)
from analytics.feature_engine import compute_rolling_features_and_save, add_market_regime_features

# defaults
FEATURE_PATH = Path("data/meta/features_rolling_20.parquet")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUT_MODEL = MODEL_DIR / "meta_model.pkl"

def _ensure_trade_date_col(df: pd.DataFrame, col_candidates=None, raise_on_missing=True):
    """
    Ensure df has a datetime column to use as 'trade_date'. Returns a copy
    (or the original) with a column 'trade_date' present and dtype datetime64[ns].
    """
    if col_candidates is None:
        col_candidates = ["trade_date", "date", "tradeDate"]

    df_local = df if isinstance(df, pd.DataFrame) else pd.DataFrame(df)

    # 1) check candidates
    for c in col_candidates:
        if c in df_local.columns:
            df_local = df_local.copy()
            df_local["trade_date"] = pd.to_datetime(df_local[c], errors="coerce")
            if df_local["trade_date"].isna().all():
                # If all coerced to NaT, ignore and continue searching
                continue
            return df_local

    # 2) check index if datetime-like
    if isinstance(df_local.index, pd.DatetimeIndex):
        df_local = df_local.copy()
        df_local["trade_date"] = pd.to_datetime(df_local.index)
        return df_local

    # 3) try to infer any column with datetime-like content
    for col in df_local.columns:
        try:
            converted = pd.to_datetime(df_local[col], errors="coerce")
            if not converted.isna().all():
                df_local = df_local.copy()
                df_local["trade_date"] = converted
                return df_local
        except Exception:
            continue

    if raise_on_missing:
        raise KeyError(
            "No trade date column found. Expected one of {}, or a datetime index. "
            "Please provide a column convertible to datetime or set the index to datetime."
            .format(col_candidates)
        )
    return df_local

def build_forward_targets_from_trades(trades_df: pd.DataFrame, window_days: int = 5) -> pd.DataFrame:
    """
    Given raw trades (one-per-executed-trade) produce forward net-PnL targets by day
    aggregated to (strategy_id,version,symbol,trade_date).
    Returns DataFrame with columns 'strategy_id','version','symbol','trade_date','target_next_window' and 'forward_net_pnl_next_window'
    """
    if trades_df is None or trades_df.empty:
        return pd.DataFrame(columns=["strategy_id", "version", "symbol", "trade_date", "target_next_window", "forward_net_pnl_next_window"])

    df = trades_df.copy()
    # ensure date / types
    if "trade_date" not in df.columns:
        if "entry_ts" in df.columns:
            df["trade_date"] = pd.to_datetime(df["entry_ts"], errors="coerce").dt.strftime("%Y-%m-%d")
        else:
            df["trade_date"] = pd.Timestamp.utcnow().strftime("%Y-%m-%d")

    df["pnl"] = pd.to_numeric(df.get("pnl", df.get("net_pnl", 0.0)), errors="coerce").fillna(0.0)
    df["trade_date_dt"] = pd.to_datetime(df["trade_date"], format="%Y-%m-%d", errors="coerce")

    targets = []
    grouped = df.groupby(["strategy_id", "version", "symbol"], sort=False)
    for (sid, ver, sym), g in grouped:
        g2 = g.sort_values("trade_date_dt")
        # daily pnl series
        daily = g2.groupby(g2["trade_date_dt"].dt.strftime("%Y-%m-%d")).agg(daily_pnl=("pnl", "sum")).reset_index().rename(columns={"trade_date_dt": "trade_date"})
        daily["strategy_id"] = sid
        daily["version"] = ver
        daily["symbol"] = sym
        daily["forward_net_pnl_next_window"] = daily["daily_pnl"].rolling(window=window_days, min_periods=1).sum().shift(- (window_days - 1)).fillna(0.0)
        daily["target_next_window"] = (daily["forward_net_pnl_next_window"] > 0).astype(int)
        targets.append(daily[["strategy_id", "version", "symbol", "trade_date", "target_next_window", "forward_net_pnl_next_window"]])

    if not targets:
        return pd.DataFrame(columns=["strategy_id", "version", "symbol", "trade_date", "target_next_window", "forward_net_pnl_next_window"])
    return pd.concat(targets, ignore_index=True)

def purged_kfold_splits_by_date(df, n_splits=5, purge_days=0):
    """
    Purged time-based KFold splits.

    Ensures the DataFrame has a 'trade_date' column (attempting to infer one)
    and then yields (train_idx, test_idx) pairs based on unique trade dates.
    If no usable trade_date can be found, raises KeyError to let caller fall back.
    """
    # Make sure we only try to coerce dates when this function is actually called.
    df = _ensure_trade_date_col(df, raise_on_missing=False)

    if "trade_date" not in df.columns:
        # No date could be inferred — raise an informative error so callers can
        # handle fallback behavior explicitly.
        raise KeyError(
            "purged_kfold_splits_by_date requires a 'trade_date' column or a datetime index "
            "that can be coerced to dates. Provide a datetime column or set the index."
        )

    # Work with a copy of the trade_date column to avoid mutating caller's df
    dates = sorted(df["trade_date"].dt.normalize().unique())
    if len(dates) < n_splits:
        raise ValueError("Not enough unique trade dates to create {} folds".format(n_splits))

    # assign date -> bucket
    from math import floor

    # Map each date to a fold index (simple round-robin by date)
    date_to_fold = {}
    for i, d in enumerate(dates):
        date_to_fold[d] = i % n_splits

    # Build index lists
    for test_fold in range(n_splits):
        test_dates = [d for d, f in date_to_fold.items() if f == test_fold]
        test_mask = df["trade_date"].dt.normalize().isin(test_dates)
        test_idx = df.index[test_mask].tolist()

        # Purge window: exclude rows within purge_days before and after test dates from training
        if purge_days and len(test_dates) > 0:
            min_test = min(test_dates)
            max_test = max(test_dates)
            purge_start = min_test - pd.Timedelta(days=purge_days)
            purge_end = max_test + pd.Timedelta(days=purge_days)
            train_mask = ~df["trade_date"].between(purge_start, purge_end)
        else:
            train_mask = ~test_mask

        train_idx = df.index[train_mask].tolist()

        yield train_idx, test_idx

def train_lightgbm(df: pd.DataFrame, target_col: str, feature_cols: list, n_splits: int = 5):
    import lightgbm as lgb
    from sklearn.metrics import roc_auc_score

    X = df[feature_cols].fillna(0.0).values
    y = df[target_col].astype(int).values
    params = {"objective": "binary", "metric": "auc", "verbosity": -1, "boosting_type": "gbdt", "num_leaves": 31}
    models = []
    aucs = []
    for fold, (tr, te) in enumerate(purged_kfold_splits_by_date(df, n_splits=n_splits, purge_days=2)):
        if len(tr) == 0 or len(te) == 0:
            logger.warning("Fold %d had empty train or test split; skipping", fold)
            continue
        dtrain = lgb.Dataset(X[tr], label=y[tr])
        dval = lgb.Dataset(X[te], label=y[te])
        booster = lgb.train(params, dtrain, num_boost_round=300, valid_sets=[dval], early_stopping_rounds=20, verbose_eval=False)
        pred = booster.predict(X[te])
        auc = roc_auc_score(y[te], pred) if len(np.unique(y[te])) > 1 else 0.5
        logger.info("Fold %d AUC %.4f", fold, auc)
        models.append(booster)
        aucs.append(auc)

    if not models:
        raise RuntimeError("No models were trained (insufficient data)")

    # wrap ensemble
    class Ensemble:
        def __init__(self, boosters):
            self.boosters = boosters

        def predict_proba(self, X_in):
            preds = np.mean([b.predict(X_in) for b in self.boosters], axis=0)
            out = np.zeros((len(preds), 2))
            out[:, 1] = preds
            out[:, 0] = 1.0 - preds
            return out

    model = Ensemble(models)
    # persist
    with open(OUT_MODEL, "wb") as fh:
        pickle.dump({"model": model, "cv_aucs": aucs}, fh)
    logger.info("Saved meta-model to %s (avg_auc=%.4f)", OUT_MODEL, float(np.mean(aucs)))
    return model, float(np.mean(aucs))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--window-days", type=int, default=5)
    parser.add_argument("--compute-features", action="store_true", help="Recompute rolling features from trade logs")
    parser.add_argument("--min-rows", type=int, default=200)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not FEATURE_PATH.exists() or args.compute_features:
        logger.info("Feature file missing or compute requested; attempting to compute")
        # read trade logs from data/trades
        # The feature module will raise if no trades found
        feats = compute_rolling_features_and_save(None, window_days=20, out_path=str(FEATURE_PATH))
    else:
        logger.info("Loading features from %s", FEATURE_PATH)
        feats = pd.read_parquet(FEATURE_PATH)

    if feats is None or feats.shape[0] < args.min_rows:
        logger.error("Insufficient feature rows (%s). Need more trades/backtests to build training set.", None if feats is None else feats.shape[0])
        return

    # Build forward targets from raw trades if possible; otherwise try to infer target column already present
    # We expect feats to contain per (strategy,version,symbol,trade_date) features.
    # If a forward target wasn't already joined, user should compute targets separately and merge before training.
    # Here we'll require the caller to supply 'target_next_window' column in the features file, or raise.
    if "target_next_window" not in feats.columns:
        logger.error("Feature file missing 'target_next_window' column. Compute forward targets and merge prior to training.")
        return

    # feature columns (explicit)
    feature_cols = [
        c for c in feats.columns
        if c not in ("strategy_id", "version", "symbol", "trade_date", "target_next_window", "forward_net_pnl_next_window")
    ]
    target_col = "target_next_window"

    model, auc = train_lightgbm(feats, target_col=target_col, feature_cols=feature_cols, n_splits=5)
    logger.info("Training complete. avg_auc=%.4f", auc)


if __name__ == "__main__":
    main()
