from __future__ import annotations

import math
from typing import Any, Dict, List

from core.v2.research.experiments.base import ResearchExperiment
from core.v2.research.contracts import ResearchExperimentError


class RegimeExperiment(ResearchExperiment):
    """
    Identifies market regime from historical snapshot data.

    This experiment is descriptive, not predictive.
    """

    def load(self) -> None:
        data = self.context.metadata.get("snapshot_data")
        if data is None:
            raise ResearchExperimentError("snapshot_data missing from metadata")

        if "prices" not in data or "returns" not in data:
            raise ResearchExperimentError(
                "snapshot_data must contain 'prices' and 'returns'"
            )

        self._prices: List[float] = list(data["prices"])
        self._returns: List[float] = list(data["returns"])

        if len(self._prices) < 5:
            raise ResearchExperimentError("Insufficient data for regime detection")

    def run(self) -> Dict[str, Any]:
        trend_strength = self._compute_trend_strength(self._prices)
        volatility = self._compute_volatility(self._returns)

        regime = self._classify(trend_strength, volatility)
        confidence = min(1.0, max(0.0, abs(trend_strength)))

        return {
            "regime": regime,
            "confidence": confidence,
            "features": {
                "trend_strength": trend_strength,
                "volatility": volatility,
            },
        }

    def evaluate(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        # No scoring here — evaluators do that later
        return raw

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_trend_strength(prices: List[float]) -> float:
        """
        Simple normalized slope proxy.
        """
        x = range(len(prices))
        mean_x = sum(x) / len(x)
        mean_y = sum(prices) / len(prices)

        num = sum((i - mean_x) * (p - mean_y) for i, p in zip(x, prices))
        den = sum((i - mean_x) ** 2 for i in x)

        return num / den if den != 0 else 0.0

    @staticmethod
    def _compute_volatility(returns: List[float]) -> float:
        mean = sum(returns) / len(returns)
        var = sum((r - mean) ** 2 for r in returns) / len(returns)
        return math.sqrt(var)

    @staticmethod
    def _classify(trend: float, vol: float) -> str:
        if abs(trend) > 0.5 and vol < 0.02:
            return "TRENDING"
        if abs(trend) < 0.2 and vol < 0.01:
            return "CALM"
        if vol > 0.03:
            return "VOLATILE"
        return "RANGING"
