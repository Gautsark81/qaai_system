# core/strategy_factory/strategy_ranker.py

from typing import List
from core.strategy_factory.strategy_candidate import StrategyCandidate


class StrategyRanker:
    """
    Ranks candidates by confidence.
    """

    @staticmethod
    def rank(candidates: List[StrategyCandidate]) -> List[StrategyCandidate]:
        return sorted(
            candidates,
            key=lambda c: c.probability_score,
            reverse=True,
        )
