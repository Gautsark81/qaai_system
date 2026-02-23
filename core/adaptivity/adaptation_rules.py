# core/adaptivity/adaptation_rules.py

from typing import Dict


class AdaptationRules:
    """
    Stateless rules that propose bounded changes.
    """

    @staticmethod
    def propose_atr_multiplier(
        current: float,
        volatility_regime: str,
    ) -> float:
        if volatility_regime == "HIGH":
            return min(current + 0.2, current * 1.2)
        if volatility_regime == "LOW":
            return max(current - 0.2, current * 0.8)
        return current

    @staticmethod
    def propose_max_symbols(
        current: int,
        liquidity_score: float,
    ) -> int:
        if liquidity_score < 0.5:
            return max(current - 5, 10)
        if liquidity_score > 0.8:
            return min(current + 5, 100)
        return current
