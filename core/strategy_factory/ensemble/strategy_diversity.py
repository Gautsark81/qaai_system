from dataclasses import dataclass
from typing import Dict, List
import math


@dataclass(frozen=True)
class StrategyDiversityResult:
    correlation_matrix: Dict[str, Dict[str, float]]
    average_correlation: Dict[str, float]
    ensemble_diversity_score: float


class StrategyDiversityEngine:

    @staticmethod
    def _correlation(x: List[float], y: List[float]) -> float:
        if len(x) != len(y) or len(x) == 0:
            return 0.0

        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)

        num = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
        den_x = math.sqrt(sum((a - mean_x) ** 2 for a in x))
        den_y = math.sqrt(sum((b - mean_y) ** 2 for b in y))

        if den_x == 0 or den_y == 0:
            return 0.0

        return num / (den_x * den_y)

    @staticmethod
    def evaluate(
        strategy_returns: Dict[str, List[float]],
    ) -> StrategyDiversityResult:

        strategy_ids = list(strategy_returns.keys())

        correlation_matrix: Dict[str, Dict[str, float]] = {}
        average_correlation: Dict[str, float] = {}

        for sid_a in strategy_ids:
            correlation_matrix[sid_a] = {}

            for sid_b in strategy_ids:
                if sid_a == sid_b:
                    corr = 1.0
                else:
                    corr = StrategyDiversityEngine._correlation(
                        strategy_returns[sid_a],
                        strategy_returns[sid_b],
                    )

                correlation_matrix[sid_a][sid_b] = corr

        for sid in strategy_ids:
            others = [
                abs(correlation_matrix[sid][other])
                for other in strategy_ids
                if other != sid
            ]
            average_correlation[sid] = (
                sum(others) / len(others) if others else 0.0
            )

        # Ensemble diversity score
        if average_correlation:
            avg_corr = sum(average_correlation.values()) / len(average_correlation)
            diversity_score = 1 - avg_corr
        else:
            diversity_score = 0.0

        return StrategyDiversityResult(
            correlation_matrix=correlation_matrix,
            average_correlation=average_correlation,
            ensemble_diversity_score=diversity_score,
        )