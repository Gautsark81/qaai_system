# modules/strategies/factory.py

from modules.strategies.spec import StrategySpec
from modules.strategies.registry import STRATEGY_REGISTRY
from modules.strategies.base import BaseStrategy


class StrategyFactory:
    @staticmethod
    def create(spec: StrategySpec) -> BaseStrategy:
        if spec.strategy_type not in STRATEGY_REGISTRY:
            raise ValueError(f"Unknown strategy_type: {spec.strategy_type}")

        strategy_cls = STRATEGY_REGISTRY[spec.strategy_type]

        strategy = strategy_cls(
            strategy_id=spec.strategy_id,
            version=spec.version,
            symbol=spec.symbol,
            timeframe=spec.timeframe,
            params=dict(spec.params),
        )

        return strategy
