# core/tournament/tournament_runner.py

from typing import Dict, List
from core.strategy.strategy_registry import StrategyRegistry
from core.tournament.tournament_engine import TournamentEngine
from core.tournament.tournament_store import TournamentStore
from core.tournament.tournament_promoter import TournamentPromoter


class TournamentRunner:
    """
    Orchestrates full tournament cycle.
    """

    def __init__(
        self,
        registry: StrategyRegistry,
        symbols: List[str],
    ):
        self.registry = registry
        self.symbols = symbols
        self.engine = TournamentEngine()
        self.store = TournamentStore()
        self.promoter = TournamentPromoter(registry, self.store)

    def run(self, strategy_objects: Dict[str, object]):
        for strategy_id, strategy in strategy_objects.items():
            metrics = self.engine.run_backtest(strategy, self.symbols)
            self.store.save_result(strategy_id, metrics)
            self.promoter.evaluate(strategy_id, metrics)
