from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class StrategyHealthHistory:
    """
    Immutable rolling history of strategy health scores.
    """

    scores: List[float]


class StrategyDecayDetector:
    """
    Detects degradation in strategy health over time.

    Advisory only.
    Deterministic.
    """

    @staticmethod
    def has_decay(history: StrategyHealthHistory) -> bool:
        if len(history.scores) < 3:
            return False

        return history.scores[-1] < history.scores[0]
