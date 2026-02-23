# core/live/live_registry.py

from core.strategy.strategy_registry import StrategyRegistry
from core.strategy.strategy_state import StrategyState


class LiveRegistry:
    """
    Tracks LIVE-eligible strategies.
    """

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def eligible(self):
        return {
            sid: meta
            for sid, meta in self.registry.all().items()
            if meta.state == StrategyState.LIVE
        }
