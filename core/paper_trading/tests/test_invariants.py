import pytest

from core.capital.allocator_v3.allocator import CapitalAllocatorV3
from core.capital.allocator_v3.contracts import StrategyCapitalProfile
from core.strategy_factory.fitness import FitnessResult
from core.regime.taxonomy import MarketRegime


def test_total_allocation_never_exceeds_one():
    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile("s1", max_allocation=0.6, min_fitness=0.1),
        StrategyCapitalProfile("s2", max_allocation=0.6, min_fitness=0.1),
    ]

    fitness = {
        "s1": FitnessResult(0.9, 0.0, True),
        "s2": FitnessResult(0.9, 0.0, True),
    }

    decision = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert decision.total_allocated <= 1.0


def test_zero_allocation_forced_when_not_eligible():
    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile("s1", max_allocation=0.5, min_fitness=0.1),
    ]

    fitness = {
        "s1": FitnessResult(0.9, 0.0, False),
    }

    decision = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    allocation = decision.allocations["s1"]
    assert allocation.allocated_fraction == 0.0
