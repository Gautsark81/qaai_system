"""
apps/run_live_dhan.py

Import-safe runtime entrypoint used by tests and demo scripts.

Exposed functions:
- build_demo_bars(symbol: str, n: int, start_price: float) -> pd.DataFrame
- run_once(bars: pd.DataFrame, model_path: Optional[str]=None, paper: bool=True, top_n: int=5) -> dict

When run as a script, will call main() which uses run_once() with generated bars.

This file includes:
- pandas 'T' -> 'min' frequency fix
- positional .iloc[-1] access fix (avoids future pandas deprecation)
- feature alignment to model's saved feature_columns (if present)
"""

from __future__ import annotations

import argparse
import logging
import pickle
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd

# 🔒 Authoritative environment source
from env_validator import CONFIG

IS_LIVE = CONFIG.mode == "live"

# ----- logging setup -----
logger = logging.getLogger("run_live_dhan")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


# ============================================================
# 🔐 SHA256 Artifact Verification (IH-1A Step 3)
# ============================================================

def _compute_sha256(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _verify_artifact_hash(path: Path) -> None:
    expected_hash = os.getenv("MODEL_ARTIFACT_SHA256", "").strip()
    actual_hash = _compute_sha256(path)

    logger.info("Model artifact SHA256: %s", actual_hash)

    if not expected_hash:
        if IS_LIVE:
            raise RuntimeError("MODEL_ARTIFACT_SHA256 not set in LIVE mode.")
        logger.warning("MODEL_ARTIFACT_SHA256 not provided; skipping verification.")
        return

    if actual_hash != expected_hash:
        msg = f"Model artifact SHA256 mismatch. Expected={expected_hash}, Actual={actual_hash}"
        if IS_LIVE:
            raise RuntimeError(msg)
        logger.warning(msg)


# ============================================================
# Demo Bars
# ============================================================

def build_demo_bars(symbol: str = "FOO", n: int = 60, start_price: float = 100.0) -> pd.DataFrame:
    rng = np.random.RandomState(0)
    idx = pd.date_range(
        pd.Timestamp.utcnow() - pd.Timedelta(minutes=n - 1),
        periods=n,
        freq="min",
    )
    open_prices = start_price + np.cumsum(rng.randn(n))
    high = open_prices + np.abs(rng.rand(n))
    low = open_prices - np.abs(rng.rand(n))
    close = open_prices + rng.randn(n) * 0.1
    volume = (rng.rand(n) * 100).astype(int)

    df = pd.DataFrame(
        {
            "timestamp": idx,
            "open": open_prices,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )
    df["symbol"] = symbol
    return df


# ============================================================
# Artifact Loading
# ============================================================

def load_model_artifact(model_path: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Load a model artifact from disk (or return None).
    Artifact shape ideally: {"model": estimator, "feature_columns": [...]}
    Tries analytics.train_meta_model.load_meta_model if available, else pickle fallback.
    """
    if not model_path:
        return None

    p = Path(model_path)
    if not p.exists():
        if IS_LIVE:
            raise RuntimeError(f"Model path not found in LIVE mode: {model_path}")
        logger.warning("Model path not found: %s", model_path)
        return None

    # 🔐 Verify integrity before loading
    _verify_artifact_hash(p)

    try:
        from analytics.train_meta_model import load_meta_model  # type: ignore
    except Exception:
        load_meta_model = None

    try:
        if load_meta_model is not None:
            art = load_meta_model(str(p))
            logger.info("Pickle loaded model artifact via analytics loader from %s (type=%s)", p, type(art))
            return art
        else:
            with p.open("rb") as fh:
                art = pickle.load(fh)
            logger.info("Pickle loaded model artifact from %s (type=%s)", p, type(art))
            return art
    except Exception as e:
        if IS_LIVE:
            raise RuntimeError(f"Failed to load model artifact in LIVE mode: {e}") from e
        logger.exception("Failed to load model artifact %s: %s", p, e)
        return None


# ============================================================
# Feature Preparation
# ============================================================

def prepare_features_for_inference(raw_bars: pd.DataFrame) -> pd.DataFrame:
    try:
        from analytics.feature_engine import compute_rolling_features  # type: ignore
        feats = compute_rolling_features(raw_bars)
        logger.info("Used repo featurizer for live features (rows=%d cols=%d)", feats.shape[0], feats.shape[1])
        return feats
    except Exception as e:
        if IS_LIVE:
            raise RuntimeError(f"Feature engine failure in LIVE mode: {e}") from e
        logger.debug("Repo featurizer not used: %s", e)

    df = raw_bars.copy()
    prev = df["close"].shift(1).bfill()
    df["ret_1"] = (df["close"] / prev - 1).fillna(0.0)
    df["volatility"] = df["ret_1"].rolling(20, min_periods=1).std().fillna(0.0)

    return df[["ret_1", "volatility"]]


# ============================================================
# Model Adapter
# ============================================================

def _build_model_adapter_from_artifact(artifact: Any):
    try:
        from strategies.strategy_engine import ModelAdapter  # type: ignore
    except Exception:
        ModelAdapter = None

    if artifact is None:
        return None

    if ModelAdapter is not None:
        try:
            return ModelAdapter.load(artifact)
        except Exception:
            try:
                if isinstance(artifact, (str, Path)):
                    return ModelAdapter.load(str(artifact))
            except Exception:
                if IS_LIVE:
                    raise RuntimeError("ModelAdapter.load failed in LIVE mode.")
                logger.exception("ModelAdapter.load failed on artifact; falling back to raw artifact.")
                return None
    return None


# ============================================================
# Feature Alignment
# ============================================================

def _align_features_for_model(feats: pd.DataFrame, artifact: Optional[Dict[str, Any]]) -> pd.DataFrame:
    if artifact and isinstance(artifact, dict) and artifact.get("feature_columns"):
        expected = list(artifact["feature_columns"])
        missing = [c for c in expected if c not in feats.columns]

        if missing:
            if IS_LIVE:
                raise RuntimeError(f"Missing required feature columns in LIVE mode: {missing}")
            logger.debug("Adding missing feature columns for inference: %s", missing)
            for c in missing:
                feats[c] = 0.0

        X = feats.reindex(columns=expected)
    else:
        if IS_LIVE:
            raise RuntimeError("Model artifact loaded without explicit feature_columns in LIVE mode.")
        logger.info("Model artifact loaded without explicit feature_columns; using heuristic alignment.")
        X = feats.select_dtypes(include=[np.number]).copy()
        if X.empty:
            X = feats.copy().apply(pd.to_numeric, errors="coerce").fillna(0.0)

    X = X.apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return X


# ============================================================
# Run Once
# ============================================================

def run_once(
    bars: Optional[pd.DataFrame] = None,
    model_path: Optional[str] = None,
    paper: bool = True,
    top_n: int = 5
) -> Dict[str, Any]:

    if bars is None:
        bars = build_demo_bars(n=60)

    feats = prepare_features_for_inference(bars)

    artifact = load_model_artifact(model_path)

    if artifact and isinstance(artifact, dict) and artifact.get("feature_columns"):
        logger.info("Model expects %d features.", len(artifact.get("feature_columns", [])))
    else:
        if not IS_LIVE:
            logger.info("Model artifact loaded without explicit feature_columns; using heuristic alignment.")

    model_adapter = _build_model_adapter_from_artifact(artifact)

    X_all = _align_features_for_model(feats, artifact)

    if X_all.shape[0] == 0:
        if IS_LIVE:
            raise RuntimeError("No features available after alignment in LIVE mode.")
        logger.info("No features available after alignment. Exiting with zero signals.")
        signals = []
    else:
        X = X_all.tail(1)
        signals = []

        if model_adapter is None:
            raw_model = None
            if isinstance(artifact, dict) and artifact.get("model") is not None:
                raw_model = artifact.get("model")

            if raw_model is None:
                if IS_LIVE:
                    raise RuntimeError("No usable model available in LIVE mode.")
                logger.info("No usable model adapter or raw model; producing zero signals.")
            else:
                try:
                    if hasattr(raw_model, "predict_proba"):
                        proba = raw_model.predict_proba(X)
                        p1 = proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]
                        for p in p1:
                            side = "BUY" if p > 0.6 else ("SELL" if p < 0.4 else "HOLD")
                            signals.append({"side": side, "size": 1.0, "confidence": float(p)})
                    elif hasattr(raw_model, "predict"):
                        y = raw_model.predict(X)
                        for yy in (y if hasattr(y, "__iter__") else [y]):
                            side = "BUY" if int(yy) == 1 else "SELL"
                            signals.append({"side": side, "size": 1.0, "confidence": 0.5})
                except Exception as e:
                    if IS_LIVE:
                        raise RuntimeError(f"Raw model inference failed in LIVE mode: {e}") from e
                    logger.exception("Raw model inference failed; no signals produced.")
        else:
            try:
                if hasattr(model_adapter, "predict_proba"):
                    proba = model_adapter.predict_proba(X)
                    p1 = proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]
                    for p in p1:
                        side = "BUY" if p > 0.6 else ("SELL" if p < 0.4 else "HOLD")
                        signals.append({"side": side, "size": 1.0, "confidence": float(p)})
                elif hasattr(model_adapter, "predict"):
                    y = model_adapter.predict(X)
                    for yy in (y if hasattr(y, "__iter__") else [y]):
                        side = "BUY" if int(yy) == 1 else "SELL"
                        signals.append({"side": side, "size": 1.0, "confidence": 0.5})
                else:
                    if IS_LIVE:
                        raise RuntimeError("Model adapter lacks predict interface in LIVE mode.")
                    logger.info("Model adapter has neither predict_proba nor predict; no signals produced.")
            except Exception as e:
                if IS_LIVE:
                    raise RuntimeError(f"Model inference failed in LIVE mode: {e}") from e
                logger.exception("Model inference failed; no signals produced.")
                signals = []

    orders = []
    if paper and signals:
        for i, sig in enumerate(signals[:top_n]):
            symbol_val = bars["symbol"].iloc[-1] if "symbol" in bars.columns else None
            orders.append({
                "order_id": f"paper-{i}",
                "symbol": symbol_val,
                "side": sig.get("side", "BUY"),
                "qty": float(sig.get("size", 1.0) or 1.0),
                "price": float(bars["close"].iloc[-1]) if not bars.empty else None,
                "status": "filled",
            })

    summary = {
        "n_signals": len(signals),
        "orders": orders,
        "backtester_summary": {
            "n_orders": len(orders),
            "total_orders": len(orders),
            "by_status": {"filled": len([o for o in orders if o.get("status") == "filled"])},
            "total_filled_qty": sum(o.get("qty", 0.0) for o in orders),
            "avg_fill_price": (
                sum(o.get("price", 0.0) * o.get("qty", 0.0) for o in orders) /
                sum(o.get("qty", 1.0) for o in orders)
            ) if orders else None,
            "orders": orders,
        },
    }

    logger.info("Run summary: %s", summary)
    return summary


def main(argv: Optional[list] = None):
    parser = argparse.ArgumentParser(prog="run_live_dhan")
    parser.add_argument("--paper", action="store_true", help="Run in paper mode (simulate orders)")
    parser.add_argument("--model", type=str, default="models/meta_model.pkl", help="Path to meta-model artifact")
    args = parser.parse_args(argv)
    bars = build_demo_bars(n=60)
    run_once(bars, model_path=args.model, paper=args.paper)


if __name__ == "__main__":
    main()