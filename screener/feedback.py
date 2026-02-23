from __future__ import annotations
from typing import Dict
import math


class ScreenerFeedback:
    """
    Maintains a per-symbol feedback weight in [0, 2] (1.0 = neutral).
    Positive outcomes push weight >1, negative outcomes push weight <1.
    Used to rescore screened symbols.
    """

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.weights: Dict[str, float] = {}  # symbol -> multiplier

    def get(self, symbol: str) -> float:
        return self.weights.get(symbol, 1.0)

    def update(self, symbol: str, realized_pnl: float, notional: float):
        # normalized outcome in [-1,1]
        if notional <= 0:
            return self.get(symbol)
        ret = max(-1.0, min(1.0, realized_pnl / notional))
        w = self.get(symbol)
        # multiplicative update, bounded (0.25 .. 4.0) to avoid explode
        factor = math.exp(self.alpha * ret)
        w_new = max(0.25, min(4.0, w * factor))
        self.weights[symbol] = w_new
        return w_new
