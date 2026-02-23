# core/capital/risk_metrics.py

from typing import Dict


class RiskMetrics:
    """
    Computes normalized risk scores.
    """

    @staticmethod
    def compute(
        ssr: float,
        max_drawdown: float,
        volatility: float,
    ) -> float:
        """
        Lower score = safer.
        """
        ssr_penalty = max(0.0, 1.0 - ssr / 100.0)
        dd_penalty = max_drawdown
        vol_penalty = volatility

        return round(
            0.4 * ssr_penalty +
            0.4 * dd_penalty +
            0.2 * vol_penalty,
            4,
        )
