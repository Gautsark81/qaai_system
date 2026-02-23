# qaai_system/analytics/allocator.py
from __future__ import annotations
import math
from typing import List, Dict, Any

def kelly_fraction(p: float, b: float = 1.0) -> float:
    """
    Kelly fraction for binary outcome with payoff multiple b (approx):
      f* = (p*(b+1) - 1) / b
    We clamp to [0, 1].
    """
    if p <= 0 or b <= 0:
        return 0.0
    num = p * (b + 1.0) - 1.0
    f = num / b
    return max(0.0, min(1.0, f))

def allocate_capital(candidates: List[Dict[str, Any]], total_risk_fraction: float = 0.1, max_per_strategy: float = 0.05) -> List[Dict[str, Any]]:
    """
    candidates: list of dict {strategy_id, version, symbol, score (probability), expected_rr (optional)}
    - total_risk_fraction: maximum fraction of account equity to risk across all strategies combined.
    - max_per_strategy: maximum fraction for any single strategy.
    Returns candidate list extended with 'alloc_fraction' per symbol-strategy.
    """
    # compute raw kelly per candidate
    raw = []
    for c in candidates:
        p = float(c.get("score", 0.0))
        # default expected payoff multiple b: we map profit_factor -> b (crudely)
        pf = float(c.get("profit_factor", 1.0))
        b = max(0.01, pf - 1.0)  # approximate
        k = kelly_fraction(p, b)
        raw.append((c, k))
    # normalize and respect total_risk_fraction
    total_k = sum([r[1] for r in raw]) or 1.0
    out=[]
    for c,k in raw:
        fraction = (k / total_k) * total_risk_fraction
        # clamp to max_per_strategy
        fraction = min(fraction, max_per_strategy)
        cc = dict(c)
        cc["alloc_fraction"] = float(fraction)
        out.append(cc)
    return out
