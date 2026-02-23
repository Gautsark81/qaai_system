from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class RedundancyPair:
    strategy_a: str
    strategy_b: str
    correlation: float


@dataclass(frozen=True)
class StrategyRedundancyResult:
    redundant_pairs: List[RedundancyPair]
    redundancy_score: float  # 0 → no redundancy, 1 → fully redundant


class StrategyRedundancyEngine:

    DEFAULT_THRESHOLD = 0.85

    @staticmethod
    def evaluate(
        correlation_matrix: Dict[str, Dict[str, float]],
        threshold: float = DEFAULT_THRESHOLD,
    ) -> StrategyRedundancyResult:

        strategy_ids = list(correlation_matrix.keys())
        redundant_pairs: List[RedundancyPair] = []

        total_pairs = 0
        redundant_count = 0

        for i in range(len(strategy_ids)):
            for j in range(i + 1, len(strategy_ids)):
                a = strategy_ids[i]
                b = strategy_ids[j]

                corr = correlation_matrix[a][b]
                total_pairs += 1

                if abs(corr) >= threshold:
                    redundant_count += 1
                    redundant_pairs.append(
                        RedundancyPair(
                            strategy_a=a,
                            strategy_b=b,
                            correlation=corr,
                        )
                    )

        redundancy_score = (
            redundant_count / total_pairs if total_pairs > 0 else 0.0
        )

        return StrategyRedundancyResult(
            redundant_pairs=redundant_pairs,
            redundancy_score=redundancy_score,
        )