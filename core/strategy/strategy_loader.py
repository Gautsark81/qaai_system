# core/strategy/strategy_loader.py

from typing import Dict
from core.strategy.strategy_registry import StrategyRegistry
from core.strategy.strategy_validator import StrategyValidator
from core.strategy.strategy_metadata import StrategyMetadata


class StrategyLoader:
    """
    Loads and validates executable strategies.
    """

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def load_executable(self) -> Dict[str, StrategyMetadata]:
        executable = {}

        for sid, meta in self.registry.all().items():
            try:
                StrategyValidator.validate_for_execution(meta)
                executable[sid] = meta
            except RuntimeError:
                continue

        return executable
