# core/strategy_factory/factory_registry.py

from datetime import datetime
from core.strategy.strategy_registry import StrategyRegistry
from core.strategy.strategy_metadata import StrategyMetadata
from core.strategy.strategy_state import StrategyState


class FactoryRegistry:
    """
    Registers generated strategies into lifecycle system.
    """

    def __init__(self):
        self.registry = StrategyRegistry()

    def register(self, strategy_id: str):
        meta = StrategyMetadata(
            strategy_id=strategy_id,
            name=strategy_id,
            version="gen_v1",
            state=StrategyState.CREATED,
            created_at=datetime.utcnow().isoformat(),
            last_updated=datetime.utcnow().isoformat(),
            notes="Auto-generated candidate",
        )
        self.registry.register(meta)
