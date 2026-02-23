# core/tournament/tournament_promoter.py

from datetime import datetime
from core.strategy.strategy_registry import StrategyRegistry
from core.strategy.strategy_state import StrategyState
from core.tournament.tournament_metrics import TournamentMetrics
from core.tournament.tournament_store import TournamentStore


class TournamentPromoter:
    SSR_THRESHOLD = 80.0

    def __init__(self, registry: StrategyRegistry, store: TournamentStore):
        self.registry = registry
        self.store = store

    def evaluate(
        self,
        strategy_id: str,
        metrics: TournamentMetrics,
    ):
        timestamp = datetime.utcnow().isoformat()

        if metrics.ssr >= self.SSR_THRESHOLD:
            self.store.log_promotion(
                f"{timestamp} | {strategy_id} | ELIGIBLE_FOR_PAPER | SSR={metrics.ssr}"
            )
            self.registry.promote(strategy_id, StrategyState.APPROVED)
        else:
            self.store.log_promotion(
                f"{timestamp} | {strategy_id} | FAILED | SSR={metrics.ssr}"
            )
