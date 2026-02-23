from dataclasses import dataclass
from typing import Dict, List
import math


@dataclass(frozen=True)
class AlphaDecayResult:
    decay_scores: Dict[str, float]   # 0 (healthy) → 1 (fully decayed)
    decay_flags: Dict[str, bool]


class AlphaDecayEngine:

    DEFAULT_DECAY_THRESHOLD = 0.6

    @staticmethod
    def _linear_slope(values: List[float]) -> float:
        n = len(values)
        if n < 2:
            return 0.0

        x_mean = (n - 1) / 2
        y_mean = sum(values) / n

        numerator = sum(
            (i - x_mean) * (v - y_mean)
            for i, v in enumerate(values)
        )
        denominator = sum(
            (i - x_mean) ** 2
            for i in range(n)
        )

        if denominator == 0:
            return 0.0

        return numerator / denominator

    @staticmethod
    def evaluate(
        strategy_returns: Dict[str, List[float]],
        decay_threshold: float = DEFAULT_DECAY_THRESHOLD,
    ) -> AlphaDecayResult:

        decay_scores: Dict[str, float] = {}
        decay_flags: Dict[str, bool] = {}

        for sid, returns in strategy_returns.items():

            if len(returns) < 4:
                decay_scores[sid] = 0.0
                decay_flags[sid] = False
                continue

            midpoint = len(returns) // 2
            first_half = returns[:midpoint]
            second_half = returns[midpoint:]

            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)

            performance_delta = first_avg - second_avg

            slope = AlphaDecayEngine._linear_slope(returns)

            # Normalize components
            delta_component = min(1.0, max(0.0, performance_delta * 50))
            slope_component = min(1.0, max(0.0, -slope * 100))

            decay_score = 0.6 * delta_component + 0.4 * slope_component

            decay_scores[sid] = decay_score
            decay_flags[sid] = decay_score >= decay_threshold

        return AlphaDecayResult(
            decay_scores=decay_scores,
            decay_flags=decay_flags,
        )