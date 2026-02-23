# signal_engine/helpers.py - lightweight compatibility helpers used by tests
from __future__ import annotations
from typing import Dict, Any, Optional

def compute_tp_sl(entry_price: float, atr: Optional[float] = None, risk_pct: Optional[float] = 0.01) -> Dict[str, Any]:
    """
    Compute trivial TP/SL given entry_price. This is intentionally conservative
    and deterministic (for tests). Replace with real logic if present.
    Returns dict with 'tp' and 'sl' keys.
    """
    try:
        p = float(entry_price)
        if atr is None or atr == 0:
            # default small offsets
            sl = p * (1.0 - (risk_pct or 0.01))
            tp = p * (1.0 + (risk_pct or 0.01) * 2.0)
        else:
            sl = p - float(atr)
            tp = p + float(atr) * 2.0
        return {"tp": float(tp), "sl": float(sl)}
    except Exception:
        return {"tp": entry_price, "sl": entry_price}

# test frameworks sometimes import the module name compute_tp_sl directly
compute_tp_sl  # exported symbol
