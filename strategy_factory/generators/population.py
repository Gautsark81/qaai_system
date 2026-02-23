from __future__ import annotations
from typing import Dict, List, Set

from qaai_system.strategy_factory.spec import StrategySpec
from qaai_system.strategy_factory.registry import StrategyRegistry


class StrategyPopulation:
    """
    Holds a population of candidate strategies.
    Enforces uniqueness and registration.
    """

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry
        self._hashes: Set[str] = set()

    def _hash_spec(self, spec: StrategySpec) -> str:
        return str(spec.entry) + str(spec.exit)

    def add(self, specs: List[StrategySpec]) -> int:
        added = 0
        for s in specs:
            h = self._hash_spec(s)
            if h in self._hashes:
                continue
            self._hashes.add(h)
            self.registry.register(s)
            added += 1
        return added
