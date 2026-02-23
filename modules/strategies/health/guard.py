# modules/strategies/health/guard.py

from modules.strategies.health.store import StrategyHealthStore
from modules.strategies.health.types import StrategyState


class StrategyKillSwitch:
    def __init__(self, store: StrategyHealthStore):
        self._store = store

    def allow_execution(self, strategy_id: str) -> bool:
        health = self._store.get(strategy_id)
        return health.state == StrategyState.ACTIVE
