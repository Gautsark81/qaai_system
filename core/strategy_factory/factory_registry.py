# core/strategy_factory/factory_registry.py

from typing import List
from core.strategy_factory.strategy_candidate import StrategyCandidate
from core.tournament.tournament_runner import TournamentRunner
from core.strategy.strategy_registry import StrategyRegistry


class FactoryRegistry:
    """
    Registers generated strategies into TOURNAMENT ONLY.
    """

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def register_candidates(
        self,
        candidates: List[StrategyCandidate],
    ):
        for c in candidates:
            self.registry.register(
                strategy_id=c.strategy_id,
                name="ELITE_INTRADAY",
                version=c.version,
            )
