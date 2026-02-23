#!/usr/bin/env python3
"""
Demo: train a tiny meta-model (or call repo trainer) and run one-shot inference.

Now includes:
 - Saves artifact as {"model": <estimator>, "feature_columns": [...]}.
 - Trainer discovery + signature-aware calls.
 - Internal featurizer + RandomForest fallback.
 - Verification that saved artifact loads.
 - PromotionRunner integration: after demo run, call PromotionRunner.process(...) to evaluate promotion rules
   and write audit (non-fatal if promotion package is missing).
"""
from __future__ import annotations
from pathlib import Path
import pickle
import logging
import sys
import importlib
import importlib.util
import inspect
from typing import Tuple, Optional, Dict, Any

import numpy as np
import pandas as pd
from pandas.api import types as pd_types

# repo root on path
REPO_ROOT = Path.cwd()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("demo_train")

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODELS_DIR / "meta_model.pkl"

# Try to import PromotionRunner (non-fatal)
try:
    from promotion.runner import PromotionRunner
except Exception:
    PromotionRunner = None

# featurizer discovery
_featurizer = None
_featurizer_candidates = [
    ("analytics.feature_engine", "compute_rolling_features"),
    ("analytics.feature_engine", "featurize_symbol"),
    ("analytics.feature_engine", "featurize"),
    ("analytics.feature_engine", "build_features"),
]
for modname, fname in _featurizer_candidates:
    try:
        m = importlib.import_module(modname)
        if hasattr(m, fname):
            _featurizer = getattr(m, fname)
            logger.info("Discovered featurizer: %s.%s", modname, fname)
            break
    except Exception:
        continue

# trainer discovery
_trainer_mod = None
try:
    _trainer_mod = importlib.import_module("analytics.train_meta_model")
except Exception:
    tfile = REPO_ROOT / "analytics" / "train_meta_model.py"
    if tfile.exists():
        spec = importlib.util.spec_from_file_location("analytics.train_meta_model", str(tfile))
        _trainer_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_trainer_mod)

_trainer_fn = None
if _trainer_mod:
    for nm in dir(_trainer_mod):
        low = nm.lower()
        if any(tok in low for tok in ("train", "fit")):
            attr = getattr(_trainer_mod, nm)
            if inspect.isfunction(attr):
                _trainer_fn = attr
                logger.info("Discovered trainer function: %s.%s", _trainer_mod.__name__, nm)
                break

# run_live module loader
def _load_run_live_module():
    try:
        import apps.run_live_dhan as m
        return m
    except Exception:
        p = REPO_ROOT / "apps" / "run_live_dhan.py"
        if not p.exists():
            raise FileNotFoundError("apps/run_live_dhan.py not found")
        spec = importlib.util.spec_from_file_location("run_live_dhan", str(p))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

_run_live_module = _load_run_live_module()

def safe_call_featurizer(featurizer_fn, df):
    required_cols = getattr(featurizer_fn, "required_columns", [])
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        logger = logging.getLogger("demo")
        logger.warning(
            "Repo featurizer failed: missing columns %s — falling back to internal featurizer",
            missing
        )
        raise ValueError("missing_cols")
    return featurizer_fn(df)

# internal featurizer
def internal_featurizer(ohlcv: pd.DataFrame, windows=None) -> pd.DataFrame:
    if windows is None:
        windows = {"short": 5, "mid": 10, "long": 20, "vol": 20}
    df = ohlcv.copy().sort_index()
    for c in ("open", "high", "low", "close", "volume"):
        if c not in df.columns:
            raise ValueError(f"Missing column '{c}' required by internal featurizer")
    df["ret_1"] = df["close"].pct_change(1).fillna(0.0)
    for name, w in windows.items():
        if name == "vol":
            continue
        df[f"ret_{w}"] = df["close"].pct_change(w).fillna(0.0)
        df[f"mom_{w}"] = df["close"] - df["close"].shift(w)
    vol_w = windows.get("vol", 20)
    df["volatility"] = df["ret_1"].rolling(vol_w, min_periods=1).std().fillna(0.0)
    prev_close = df["close"].shift(1).bfill()
    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - prev_close).abs()
    tr3 = (df["low"] - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["atr"] = tr.rolling(vol_w, min_periods=1).mean().fillna(0.0)
    df["atr_ratio"] = (df["atr"] / df["close"].replace({0: np.nan})).fillna(0.0)
    df["vol_mean"] = df["volume"].rolling(vol_w, min_periods=1).mean().fillna(1.0)
    df["vol_ratio"] = (df["volume"] / df["vol_mean"]).fillna(0.0)
    cols = [c for c in df.columns if c not in ("open", "high", "low", "close", "volume")]
    out = df[cols].copy()
    if "symbol" in df.columns:
        out["symbol"] = df["symbol"]
    return out

# internal trainer (sklearn)
def internal_train_and_save(X: pd.DataFrame, y: pd.Series, model_path: Path = MODEL_PATH) -> Path:
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)),
    ])
    pipeline.fit(X, y)
    artifact = {"model": pipeline, "feature_columns": list(X.columns)}
    with open(model_path, "wb") as fh:
        pickle.dump(artifact, fh)
    logger.info("Saved internal RandomForest artifact (with feature_columns) to %s", model_path)
    return model_path

# synthetic bars
def synthetic_bars(symbol="FOO", n=500, start_price=100.0) -> pd.DataFrame:
    idx = pd.date_range(pd.Timestamp.utcnow() - pd.Timedelta(minutes=n - 1), periods=n, freq="min")
    prices = [start_price + 0.01 * i + (np.sin(i / 10.0) * 0.2) for i in range(n)]
    df = pd.DataFrame({
        "open": prices,
        "high": [p * 1.0008 for p in prices],
        "low": [p * 0.9992 for p in prices],
        "close": prices,
        "volume": [100 + (i % 50) for i in range(n)],
    }, index=idx)
    df.index.name = "timestamp"
    df["symbol"] = symbol
    return df

# build training dataset - numeric X and y
def build_training_dataset(bars: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    feats = None
    if _featurizer is not None:
        try:
            feats = _featurizer(bars)
        except Exception as e:
            logger.warning("Repo featurizer failed: %s — falling back to internal featurizer", e)
            feats = None
    if feats is None:
        feats = internal_featurizer(bars)
        logger.info("Using internal featurizer for training")

    df = bars.copy()
    if "trade_date" not in df.columns:
        try:
            df["trade_date"] = pd.to_datetime(df.index).normalize()
        except Exception:
            df["trade_date"] = pd.Timestamp.utcnow().normalize()

    df["ret_fwd_5"] = df["close"].pct_change(5).shift(-5)
    merged = feats.join(df[["ret_fwd_5", "trade_date"]], how="left")
    merged["label"] = (merged["ret_fwd_5"] > 0).astype(int)
    merged = merged.dropna(subset=["label"])

    X_candidate = merged.drop(columns=["label"], errors="ignore")
    numeric_cols = [c for c in X_candidate.columns if pd_types.is_numeric_dtype(X_candidate[c].dtype)]
    if not numeric_cols:
        raise RuntimeError("No numeric features available after featurization")
    X = X_candidate[numeric_cols].copy()
    y = merged.loc[X.index, "label"].astype(int)

    mask = X.isna().any(axis=1) | y.isna()
    X = X[~mask]
    y = y[~mask]
    return X, y

# train-and-save (signature-aware); ensures we save feature_columns meta
def train_and_save() -> Path:
    bars = synthetic_bars(n=600)
    X, y = build_training_dataset(bars)
    logger.info("Training set rows=%d features=%d", len(X), X.shape[1])
    if len(X) < 20:
        raise RuntimeError("Too few rows to train")

    model_path = MODEL_PATH
    result = None

    # Try repo trainer
    if _trainer_fn is not None:
        try:
            sig = inspect.signature(_trainer_fn)
            params = list(sig.parameters.keys())
            df_train = pd.concat([X, y.rename("label")], axis=1)
            kwargs = {}
            if "feature_cols" in params:
                kwargs["feature_cols"] = list(X.columns)
            if "target_col" in params:
                kwargs["target_col"] = "label"
            if "label_col" in params:
                kwargs["label_col"] = "label"
            if "model_path" in params:
                kwargs["model_path"] = str(model_path)
            logger.info("Invoking repo trainer %s with kwargs=%s", _trainer_fn.__name__, kwargs)
            result = _trainer_fn(df_train, **kwargs)
        except Exception as e:
            logger.exception("Repo trainer invocation failed (%s). Falling back to internal trainer.", e)
            result = None

    # If trainer returned something, persist with feature_columns if possible
    if result is not None:
        if model_path.exists():
            logger.info("Repo trainer saved model artifact at %s", model_path)
        else:
            if isinstance(result, dict) and "model" in result:
                # add feature_columns if not present
                if "feature_columns" not in result:
                    result["feature_columns"] = list(X.columns)
                with open(model_path, "wb") as fh:
                    pickle.dump(result, fh)
                logger.info("Saved trainer-returned dict to %s (added feature_columns)", model_path)
            else:
                try:
                    import sklearn  # type: ignore
                    artifact = {"model": result, "feature_columns": list(X.columns)}
                    with open(model_path, "wb") as fh:
                        pickle.dump(artifact, fh)
                    logger.info("Saved trainer-returned estimator to %s (with feature_columns)", model_path)
                except Exception:
                    logger.warning("Trainer returned an object that couldn't be serialized; falling back to internal trainer")
                    result = None

    # fallback internal trainer
    if result is None:
        logger.info("Training internal RandomForest fallback and saving to %s", model_path)
        internal_train_and_save(X, y, model_path)

    # verify artifact exists and loads
    if not model_path.exists():
        raise FileNotFoundError(f"Model file missing after training: {model_path}")
    try:
        try:
            from analytics.train_meta_model import load_meta_model  # type: ignore
            art = load_meta_model(str(model_path))
        except Exception:
            with open(model_path, "rb") as fh:
                art = pickle.load(fh)
        # normalize artifact: ensure it has model & feature_columns
        if isinstance(art, dict) and "model" in art:
            if "feature_columns" not in art:
                art["feature_columns"] = list(X.columns)
                with open(model_path, "wb") as fh:
                    pickle.dump(art, fh)
        else:
            # wrap non-dict estimator
            art = {"model": art, "feature_columns": list(X.columns)}
            with open(model_path, "wb") as fh:
                pickle.dump(art, fh)
        logger.info("Verified model artifact at %s (feature_columns=%d)", model_path, len(art.get("feature_columns", [])))
    except Exception as e:
        raise RuntimeError(f"Saved model artifact exists but failed to load/normalize: {e}") from e

    return model_path

def _extract_metrics_from_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a conservative promotion metrics dict from run summary.
    Tries to extract likely keys (win_rate, pf, trades, drawdown). Falls back to defaults.
    """
    metrics: Dict[str, Any] = {}
    if not isinstance(summary, dict):
        return {"win_rate": 0.5, "pf": 1.0, "trades": 0, "drawdown": 0.0}

    # direct metrics section
    if "metrics" in summary and isinstance(summary["metrics"], dict):
        metrics.update(summary["metrics"])

    # backtester summary heuristics
    b = summary.get("backtester_summary") or summary.get("backtest") or {}
    if isinstance(b, dict):
        # trades
        trades = b.get("total_orders") or b.get("n_orders") or b.get("total_filled_qty") or b.get("trades") or b.get("n_trades")
        if trades is not None:
            try:
                metrics.setdefault("trades", int(trades))
            except Exception:
                pass
        # profit factor / pf (if provided)
        pf = b.get("pf") or b.get("profit_factor")
        if pf is not None:
            try:
                metrics.setdefault("pf", float(pf))
            except Exception:
                pass
        # drawdown
        dd = b.get("drawdown") or b.get("max_drawdown")
        if dd is not None:
            try:
                metrics.setdefault("drawdown", float(dd))
            except Exception:
                pass

    # attempt to infer trades from top-level fields
    if "n_signals" in summary and metrics.get("trades") is None:
        try:
            metrics["trades"] = int(summary.get("n_signals", 0))
        except Exception:
            pass

    # win_rate best-effort: if orders present and status info exists, compute simple hit rate
    orders = None
    if "orders" in summary and isinstance(summary["orders"], list):
        orders = summary["orders"]
    elif isinstance(b, dict) and isinstance(b.get("orders"), list):
        orders = b.get("orders")

    if orders is not None and metrics.get("win_rate") is None:
        # If orders contain 'side' and some 'pl' field, calculate simplistic win-rate
        wins = 0
        tot = 0
        for o in orders:
            if not isinstance(o, dict):
                continue
            tot += 1
            # simple heuristic: if order has 'pnl' or 'pl' or 'profit' fields
            for k in ("pnl", "pl", "profit", "pnl_realized"):
                if k in o:
                    try:
                        if float(o[k]) > 0:
                            wins += 1
                    except Exception:
                        pass
                    break
        if tot > 0:
            metrics["win_rate"] = float(wins) / float(tot)

    # fill defaults
    metrics.setdefault("win_rate", 0.5)
    metrics.setdefault("pf", 1.0)
    metrics.setdefault("trades", int(metrics.get("trades", 0)))
    metrics.setdefault("drawdown", float(metrics.get("drawdown", 0.0)))
    return metrics

# run demo
def run_demo(use_model: Optional[str] = None):
    model_path = train_and_save()
    bars = synthetic_bars(n=120)
    summary = _run_live_module.run_once(bars, model_path=str(model_path), paper=True, top_n=5)
    logger.info("Demo summary: %s", summary)
    print("DEMO SUMMARY:", summary)

    # --- PromotionRunner integration (non-fatal) ---
    # Attempt to run promotion evaluation & write audit (if PromotionRunner is available)
    if PromotionRunner is not None:
        try:
            # Build a light-weight engine config; tune to your production rules if desired
            engine_cfg = {
                "defaults": {"min_trades": 20, "max_drawdown_abs": 0.35},
                "rules": [
                    {
                        "name": "fast_promote",
                        "priority": 10,
                        "action": "PROMOTE",
                        "conditions": {"win_rate": {">=": 0.6}, "pf": {">=": 1.6}, "trades": {">=": 50}},
                    },
                    {
                        "name": "stable_promote",
                        "priority": 5,
                        "action": "PROMOTE",
                        "conditions": {"win_rate": {">=": 0.55}, "pf": {">=": 1.4}, "trades": {">=": 100}},
                    },
                ],
            }
            audit_path = "promotion/audit.jsonl"
            runner = PromotionRunner(engine_config=engine_cfg, audit_path=audit_path)

            metrics_for_promo = _extract_metrics_from_summary(summary)
            extra = {"source": "demo_train_and_run", "model_path": str(model_path)}
            decision = runner.process(strategy_id="demo_strategy", metrics=metrics_for_promo, extra=extra)
            # Log decision for visibility
            logger.info("Promotion decision: %s", decision)
            print("Promotion decision:", decision)
        except Exception:
            logger.exception("PromotionRunner invocation failed; continuing demo")
    else:
        logger.debug("PromotionRunner not available - skipping promotion evaluation")

    return summary

# CLI
def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Demo train + run")
    p.add_argument("--no-train", action="store_true", help="Skip training; use existing model at models/meta_model.pkl")
    p.add_argument("--model", type=str, default=str(MODEL_PATH), help="Model pickle path")
    args = p.parse_args(argv)

    if args.no_train:
        if not Path(args.model).exists():
            logger.error("Requested --no-train but model not found: %s", args.model)
            return 2
        bars = synthetic_bars(n=120)
        summary = _run_live_module.run_once(bars, model_path=args.model, paper=True, top_n=5)
        print("DEMO SUMMARY:", summary)
        return 0

    run_demo()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
