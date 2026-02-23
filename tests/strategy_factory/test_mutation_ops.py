from __future__ import annotations
from typing import List
import random

from qaai_system.strategy_factory.spec import StrategySpec
from qaai_system.strategy_factory.evolution.mutation_ops import (
    mutate_entry_logic,
)
from qaai_system.strategy_factory.evolution.lineage import spawn_lineage


class MutationEngine:
    """
    Deterministic strategy evolution engine.
    """

    def __init__(self, *, seed: int | None = None):
        self._rng = random.Random(seed)

    def mutate(self, parents: List[StrategySpec]) -> List[StrategySpec]:
        children: List[StrategySpec] = []

        for p in parents:
            mutated_entry = mutate_entry_logic(p.entry)

            lineage = spawn_lineage(
                p.lineage or {},
                mutation_type="entry_logic",
            )

            child = StrategySpec(
                family=p.family,
                timeframe=p.timeframe,
                indicators=p.indicators,
                entry=mutated_entry,
                exit=p.exit,
                lineage=lineage,
            )

            children.append(child)

        return children
