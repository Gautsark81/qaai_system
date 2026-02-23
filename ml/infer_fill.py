# ml/infer_fill.py
"""
Fill-model utilities and wrapper.

This file includes:
- existing FillModel class (loads joblib model artifacts and exposes predict_proba_for_order)
- CLI for ad-hoc calls (unchanged)
- NEW: module-level model registry functions:
    - load_model(path_or_obj)
    - clear_model()
    - infer_fill(order, bar, remaining_qty)  <-- used by FillModelAdapter
The infer_fill function returns a dict:
    {"filled_qty": float, "avg_price": float, "status": "filled"|"partial"|"open"}
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional
import joblib
import numpy as np
import pandas as pd
import logging
import argparse
import threading
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------
# Original FillModel code (preserved)
# ---------------------------

def _build_feature_row(order: Dict[str, Any], features: List[str]) -> pd.DataFrame:
    """
    Given an order dict, produce a single-row DataFrame with the expected feature columns.
    This should mirror the feature engineering in the training script.
    """
    # normalize common input keys (safe and permissive)
    symbol = order.get("symbol", "UNKNOWN")
    # allow both 'quantity' and 'qty'
    qty_raw = order.get("quantity", order.get("qty", 0))
    try:
        qty = float(qty_raw or 0)
    except Exception:
        qty = 0.0

    try:
        price = float(order.get("price", 0.0) or 0.0)
    except Exception:
        price = 0.0

    side_buy = 1 if order.get("side", "buy") == "buy" else 0

    # timestamp handling: robustly handle NaT / missing timestamp
    ts_raw = order.get("timestamp", order.get("ts", pd.NaT))
    ts = pd.to_datetime(ts_raw, errors="coerce")
    if pd.isna(ts):
        hour = 0
        weekday = 0
    else:
        # ts may be a pandas Timestamp or Python datetime
        hour = int(getattr(ts, "hour", 0) or 0)
        weekday = int(getattr(ts, "weekday", 0) or 0)

    # account nav may be passed as 'account_nav' or 'nav'
    try:
        account_nav = float(order.get("account_nav", order.get("nav", 0.0) or 0.0))
    except Exception:
        account_nav = 0.0

    try:
        last_price = float(order.get("last_price", price) or price)
    except Exception:
        last_price = price

    price_diff = last_price - price
    pct_diff = price_diff / (last_price if last_price != 0 else 1.0)
    is_aggr_buy = int(price >= last_price)
    is_aggr_sell = int(price <= last_price)
    spread_abs = abs(price_diff)
    qty_nav_ratio = qty / (account_nav if account_nav != 0 else 1.0)

    # placeholder symbol-level stats (may be missing)
    try:
        symbol_fill_rate = float(order.get("symbol_fill_rate", 0.0) or 0.0)
    except Exception:
        symbol_fill_rate = 0.0
    try:
        symbol_avg_qty = float(order.get("symbol_avg_qty", qty) or qty)
    except Exception:
        symbol_avg_qty = qty
    try:
        symbol_vol = float(order.get("symbol_volatility", 0.0) or 0.0)
    except Exception:
        symbol_vol = 0.0

    # Construct a canonical row containing both variants of common feature names
    row = {
        # both naming conventions supported
        "quantity": qty,
        "qty": qty,
        "price": price,
        "side_buy": side_buy,
        "hour": hour,
        "weekday": weekday,
        "account_nav": account_nav,
        "nav": account_nav,
        "last_price": last_price,
        "price_diff": price_diff,
        "pct_diff": pct_diff,
        "is_aggressive_buy": is_aggr_buy,
        "is_aggressive_sell": is_aggr_sell,
        "spread_abs": spread_abs,
        "qty_nav_ratio": qty_nav_ratio,
        "symbol_fill_rate": symbol_fill_rate,
        "symbol_avg_qty": symbol_avg_qty,
        "symbol_volatility": symbol_vol,
    }

    # Build output row honoring the model's expected feature list. Missing features get 0.0
    data = {f: float(row.get(f, 0.0)) for f in features}
    return pd.DataFrame([data])


class FillModel:
    def __init__(self, model_path: str = "models/fill_model_v3.pkl"):
        # Accept many common locations so CLI/tests work on Windows and in the sandbox.
        tried = []
        candidate_paths = []
        # user-supplied path first
        candidate_paths.append(Path(model_path))
        # relative path inside repo (common place where training saved models)
        candidate_paths.append(Path.cwd() / "models" / Path(model_path).name)
        # also consider a common v2 filename fallback
        candidate_paths.append(Path.cwd() / "models" / "fill_model.pkl")
        # sandbox path used by assistant environment
        candidate_paths.append(Path("/mnt/data/models") / Path(model_path).name)

        found = None
        for p in candidate_paths:
            tried.append(str(p))
            if p.exists():
                found = p
                break

        if found is None:
            # fallback: try to find any model in ./models/ with prefix 'fill_model'
            models_dir = Path.cwd() / "models"
            if models_dir.exists():
                for candidate in models_dir.iterdir():
                    if candidate.name.startswith("fill_model") and candidate.suffix in (
                        ".pkl",
                        ".joblib",
                    ):
                        found = candidate
                        break
            if found is None:
                raise FileNotFoundError(f"Model file not found. Tried: {tried}")

        self.model_path = found
        obj = joblib.load(self.model_path)
        # expecting {"model": scikit-learn estimator, "features": [...]}
        if isinstance(obj, dict) and "model" in obj and "features" in obj:
            self.model = obj["model"]
            self.features = list(obj["features"])
        else:
            # backward compatibility: plain estimator
            self.model = obj
            # best-effort default feature list (v1)
            self.features = [
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
        logger.info(
            "Loaded model from %s (features: %s)", self.model_path, self.features
        )

    def predict_proba_for_order(self, order: Dict[str, Any]) -> float:
        """Return probability of fill (float in [0,1]) for a single order dict."""
        df = _build_feature_row(order, self.features)
        proba = None
        try:
            if hasattr(self.model, "predict_proba"):
                proba = float(self.model.predict_proba(df.values)[:, 1][0])
            else:
                # fallback: decision_function or predict
                if hasattr(self.model, "decision_function"):
                    score = float(self.model.decision_function(df.values)[0])
                    proba = 1.0 / (1.0 + np.exp(-score))
                else:
                    pred = self.model.predict(df.values)[0]
                    proba = float(pred)
        except Exception as e:
            logger.exception("Model inference failed: %s", e)
            # safe fallback: neutral probability 0.5
            proba = 0.5
        return proba


# ---------------------------
# NEW: module-level model registry + infer_fill wrapper
# ---------------------------

_MODEL_LOCK = threading.Lock()
_MODEL = None  # either FillModel instance or an arbitrary model object compatible with FillModel

def load_model(path_or_obj: Optional[Any]):
    """
    Register a model for runtime use by infer_fill.
    Accepts:
      - a FillModel instance
      - a path to a joblib/pickle file (loads into FillModel if the file contains a dict with 'model'/'features')
      - a raw estimator object (best-effort; must support predict/probability methods)
    """
    global _MODEL
    with _MODEL_LOCK:
        if path_or_obj is None:
            _MODEL = None
            return
        # If user passes a FillModel instance, use it directly
        if isinstance(path_or_obj, FillModel):
            _MODEL = path_or_obj
            return
        # If it's a path string, try to construct FillModel with it
        if isinstance(path_or_obj, str) or isinstance(path_or_obj, Path):
            # try building FillModel with the path as model_path (it will search)
            _MODEL = FillModel(str(path_or_obj))
            return
        # If it's a raw object (estimator), wrap with a thin adapter using default features
        try:
            # Build a thin wrapper that exposes predict_proba_for_order like FillModel
            class _Adapter:
                def __init__(self, estimator):
                    self.estimator = estimator
                    # best-effort feature list (same as above)
                    self.features = [
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

                def predict_proba_for_order(self, order):
                    df = _build_feature_row(order, self.features)
                    if hasattr(self.estimator, "predict_proba"):
                        return float(self.estimator.predict_proba(df.values)[:, 1][0])
                    if hasattr(self.estimator, "decision_function"):
                        score = float(self.estimator.decision_function(df.values)[0])
                        return 1.0 / (1.0 + np.exp(-score))
                    return float(self.estimator.predict(df.values)[0])

            _MODEL = _Adapter(path_or_obj)
            return
        except Exception as e:
            raise RuntimeError("Failed to register model: %s" % e) from e

def clear_model():
    """Clear the registered model (set to None)."""
    global _MODEL
    with _MODEL_LOCK:
        _MODEL = None

def _call_registered_model(order: Dict[str, Any]) -> Optional[float]:
    """
    If a model is registered, call it to obtain a fill probability [0,1].
    Returns None if no model registered or model fails.
    """
    global _MODEL
    with _MODEL_LOCK:
        model = _MODEL
    if model is None:
        return None
    try:
        # Prefer FillModel-like API
        if hasattr(model, "predict_proba_for_order"):
            return float(model.predict_proba_for_order(order))
        # Try common estimator methods via adapter
        if hasattr(model, "predict_proba"):
            df = _build_feature_row(order, getattr(model, "features", []))
            return float(model.predict_proba(df.values)[:, 1][0])
        # fallback to predict or decision_function
        if hasattr(model, "decision_function"):
            df = _build_feature_row(order, getattr(model, "features", []))
            score = float(model.decision_function(df.values)[0])
            return 1.0 / (1.0 + np.exp(-score))
        if hasattr(model, "predict"):
            df = _build_feature_row(order, getattr(model, "features", []))
            return float(model.predict(df.values)[0])
    except Exception:
        logger.exception("Registered model failed during inference; falling back to heuristic")
    return None

def infer_fill(order: Any, bar: Dict[str, Any], remaining_qty: Optional[float] = None) -> Dict[str, Any]:
    """
    Main entry point expected by FillModelAdapter.
    Returns a dict: {"filled_qty": float, "avg_price": float, "status": "filled"|"partial"|"open"}

    Behavior:
    - If a registered model is present, use its predicted probability p in [0,1] and compute:
        filled_qty = min(remaining_qty, p * remaining_qty)  # i.e. expected fraction of remaining filled
      (This is deterministic and safe.)
    - If no model is present or it fails, fall back to a deterministic heuristic:
        default_participation = 0.1 -> target_fill = min(remaining_qty, participation * bar.volume)
    """
    if remaining_qty is None:
        remaining_qty = float(getattr(order, "qty", order.get("qty", 0) if isinstance(order, dict) else 0.0))
    remaining_qty = float(remaining_qty)

    # Ensure bar is dict-like and extract close & volume
    vol = float(bar.get("volume", 0.0) or 0.0)
    close_price = float(bar.get("close", getattr(order, "price", order.get("price", 0.0) if isinstance(order, dict) else 0.0) or 0.0))

    # Try model
    p = _call_registered_model(order if isinstance(order, dict) else vars(order) if hasattr(order, "__dict__") else order)
    if p is not None:
        # clamp p
        try:
            p = float(p)
        except Exception:
            p = 0.0
        if p < 0.0:
            p = 0.0
        if p > 1.0:
            p = 1.0
        # deterministic mapping: expected filled fraction = p -> filled_qty = remaining_qty * p
        filled = float(min(remaining_qty, remaining_qty * p))
        status = "filled" if (remaining_qty - filled) <= 1e-9 else ("partial" if filled > 0 else "open")
        return {"filled_qty": filled, "avg_price": close_price, "status": status}

    # Heuristic fallback (deterministic)
    default_participation = 0.1
    per_bar_capacity = default_participation * vol
    target_fill = min(remaining_qty, per_bar_capacity)
    filled = float(target_fill)
    if filled <= 0:
        return {"filled_qty": 0.0, "avg_price": close_price, "status": "open"}
    status = "filled" if (remaining_qty - filled) <= 1e-9 else "partial"
    return {"filled_qty": filled, "avg_price": close_price, "status": status}


# ---------------------------
# CLI (unchanged)
# ---------------------------

def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--model",
        default="/mnt/data/models/fill_model.pkl",
        help="Path to model joblib",
    )
    p.add_argument("--symbol", required=True)
    p.add_argument("--side", default="buy")
    p.add_argument("--qty", type=float, default=1.0)
    p.add_argument("--price", type=float, default=0.0)
    p.add_argument("--nav", type=float, default=0.0)
    p.add_argument("--last_price", type=float, default=None)
    return p.parse_args()


def _cli_main():
    args = _parse_args()
    model = FillModel(args.model)
    order = {
        "symbol": args.symbol,
        "side": args.side,
        "quantity": args.qty,
        "price": args.price,
        "account_nav": args.nav,
    }
    if args.last_price is not None:
        order["last_price"] = args.last_price
    prob = model.predict_proba_for_order(order)
    print(f"p(fill) = {prob:.4f}")


if __name__ == "__main__":
    _cli_main()
