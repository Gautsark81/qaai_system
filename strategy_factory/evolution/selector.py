from __future__ import annotations
from typing import List
import random

from qaai_system.strategy_factory.spec import StrategySpec


def select_parents(
    population: List[StrategySpec],
    *,
    k: int,
) -> List[StrategySpec]:
    """
    Temporary selector.
    Later replaced by fitness-weighted scoring.
    """
    if len(population) <= k:
        return population
    return random.sample(population, k)
