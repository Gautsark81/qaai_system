# modules/backtester/infer_fill_adapter.py
from __future__ import annotations
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MLInferFillAdapter:
    """
    Adapter that exposes predict_fill(symbol, price, qty, side, ts) -> p_fill
    Wraps your ml.infer_fill API if available; otherwise falls back to heuristic.
    """
    def __init__(self, model=None):
        # model can be an object exposing predict_proba(...) or similar.
        self._model = model
        # try to lazy-import the project's infer_fill helper if model not provided
        if self._model is None:
            try:
                from ml.infer_fill import infer_fill  # adjust import path if different
                self._infer_fn = infer_fill
                logger.info("MLInferFillAdapter: using ml.infer_fill.infer_fill")
            except Exception as e:
                logger.warning("MLInferFillAdapter: ml.infer_fill not available, falling back to heuristic: %s", e)
                self._infer_fn = None
        else:
            self._infer_fn = None

    def predict_fill(self, symbol: str, price: float, qty: float, side: str, ts=None) -> float:
        # If we have a model or function, try to use it (guard exceptions)
        try:
            if self._model is not None:
                # assume model.predict_proba returns [[p0, p1]] or model.predict returns probability
                if hasattr(self._model, "predict_proba"):
                    p = self._model.predict_proba([[qty, price, 1 if side.upper()=="BUY" else 0]])[0][1]
                    return float(max(0.0, min(1.0, p)))
                if hasattr(self._model, "predict"):
                    p = self._model.predict([[qty, price, 1 if side.upper()=="BUY" else 0]])
                    return float(max(0.0, min(1.0, p)))
            if self._infer_fn is not None:
                # infer_fill(symbol, price, qty, side) -> probability (your project may have a different signature)
                p = self._infer_fn(symbol=symbol, price=price, qty=qty, side=side)
                return float(max(0.0, min(1.0, p)))
        except Exception as e:
            logger.exception("infer_fill adapter error: %s", e)
        # fallback simple heuristic: smaller orders fill more often
        if qty <= 5:
            return 0.9
        if qty <= 20:
            return 0.6
        return 0.2
