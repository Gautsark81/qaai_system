# core/strategy/kill_switch.py

from core.strategy.strategy_registry import StrategyRegistry
from core.strategy.strategy_state import StrategyState


class StrategyKillSwitch:
    """
    Hard kill. No recovery.
    """

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def kill(self, strategy_id: str, reason: str = ""):
        meta = self.registry.get(strategy_id)
        killed = meta.promote(StrategyState.KILLED)
        self.registry._strategies[strategy_id] = killed
        self.registry._persist()
