# modules/backtester/fill_model_adapter.py
"""
Adapter that selects between an ML fill model and a fallback volumetric slippage model.

Behavior change: if no ml_infer_fn is provided explicitly, the adapter will attempt to import
ml.infer_fill.infer_fill and use it automatically (so wiring happens without changing call sites).
"""

from typing import Callable, Dict, Any, Tuple, Optional
from modules.backtester.volumetric_slippage import VolumetricSlippage, Order

def _try_import_default_ml_hook():
    try:
        # lazy import to avoid heavy modules at import time
        from ml.infer_fill import infer_fill
        return infer_fill
    except Exception:
        return None

class FillModelAdapter:
    def __init__(self, ml_infer_fn: Optional[Callable] = None, volumetric_kwargs: Optional[Dict] = None):
        """
        ml_infer_fn: optional callable(order, bar, remaining_qty) -> dict or tuple
                     If None, adapter will attempt to import ml.infer_fill.infer_fill
        volumetric_kwargs: params passed to VolumetricSlippage constructor
        """
        self.ml_infer_fn = ml_infer_fn or _try_import_default_ml_hook()
        self.volumetric = VolumetricSlippage(**(volumetric_kwargs or {}))

    def fill(self, order: Order, bar: Dict[str, Any], remaining_qty: float = None) -> Tuple[float, float, str]:
        # Prefer ML hook if available
        if callable(self.ml_infer_fn):
            try:
                res = self.ml_infer_fn(order, bar, remaining_qty)
                # Accept either tuple (filled, price, status) or dict
                if isinstance(res, (list, tuple)) and len(res) >= 3:
                    return float(res[0]), float(res[1]), str(res[2])
                if isinstance(res, dict):
                    return float(res.get("filled_qty", 0.0)), float(res.get("avg_price", order.price)), str(res.get("status", "open"))
                # Otherwise, invalid return -> fall back
            except Exception:
                # Do not propagate; fallback to volumetric
                pass

        # Fallback
        return self.volumetric.fill(order, bar, remaining_qty=remaining_qty)
