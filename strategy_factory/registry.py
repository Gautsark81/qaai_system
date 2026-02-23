from __future__ import annotations
from typing import Dict
from .spec import StrategySpec


class StrategyRegistry:
    """
    In-memory registry (Phase C1).
    Will become persistent in Phase C2.
    """

    def __init__(self):
        self._store: Dict[str, StrategySpec] = {}

    def register(self, spec: StrategySpec) -> None:
        self._store[spec.strategy_id] = spec

    def get(self, strategy_id: str) -> StrategySpec:
        return self._store[strategy_id]

    def all(self):
        return list(self._store.values())
