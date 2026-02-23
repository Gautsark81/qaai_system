from typing import Iterable, List
from domain.strategy_factory.strategy_candidate import StrategyCandidate


class FactoryOutputFilter:
    """
    Filters strategy candidates based on governance.
    """

    @staticmethod
    def eligible_only(
        candidates: Iterable[StrategyCandidate],
    ) -> List[StrategyCandidate]:
        return [c for c in candidates if c.eligible]
