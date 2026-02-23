"""
Position sizing utilities.

Implements:
- volatility_target_size(volatility, target_vol): converts volatility measure -> fraction of capital
- kelly_position_size(edge, win_prob, odds, max_fraction): conservative Kelly fraction with shrinkage
"""

from __future__ import annotations
from typing import Optional
import math
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def volatility_target_size(volatility: float, target_vol: float = 0.02, capital: float = 1.0, vol_floor: float = 1e-6, max_fraction: float = 0.2) -> float:
    """
    Convert a volatility metric (e.g., atr_ratio or estimated vol) into a position fraction.
    - volatility: higher -> smaller size
    - target_vol: desired portfolio vol per position
    - capital: nominal (1.0 => fraction)
    Returns fraction of capital.
    """
    vol = max(volatility, vol_floor)
    # naive mapping: size_fraction = target_vol / vol, then clamp
    fraction = float(target_vol) / float(vol)
    fraction = max(0.0, min(float(max_fraction), fraction))
    return fraction


def kelly_position_size(edge: float, win_prob: float, odds: float = 1.0, max_fraction: float = 0.05, shrink: float = 0.5) -> float:
    """
    Kelly fraction for binary outcomes:
      f* = (bp - q) / b where b = odds, p = win_prob, q = 1-p
    We use edge directly and apply shrink factor and clamp.

    - edge: expected edge (mean return per unit risk), can also be p - q for binary-like
    - win_prob: probability of win (0..1)
    - odds: payout odds (1 for symmetric)
    - shrink: fraction to shrink Kelly to reduce risk
    """
    p = float(max(0.0, min(1.0, win_prob)))
    q = 1.0 - p
    b = float(max(1e-6, odds))
    try:
        # if caller provides edge as p - q, convert to Kelly approximate
        # safe fallback: compute using p and b
        f = (b * p - q) / b
    except Exception:
        f = 0.0
    # shrink and clamp
    f = float(f) * float(shrink)
    if math.isnan(f) or f <= 0:
        return 0.0
    return max(0.0, min(float(max_fraction), f))
