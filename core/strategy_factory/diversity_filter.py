# core/strategy_factory/diversity_filter.py

from typing import List
from core.strategy_factory.strategy_spec import StrategySpec


class DiversityFilter:
    """
    Prevents duplicate or overly similar strategies.
    """

    @staticmethod
    def is_diverse(
        candidate: StrategySpec,
        existing: List[StrategySpec],
    ) -> bool:
        for s in existing:
            if (
                s.archetype == candidate.archetype
                and s.timeframe == candidate.timeframe
                and s.indicators == candidate.indicators
            ):
                return False
        return True
