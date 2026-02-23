from core.capital.allocator_v3.allocator import CapitalAllocatorV3
from core.capital.allocator_v3.contracts import StrategyCapitalProfile
from core.capital.contracts.fitness import CapitalFitness
from core.regime.taxonomy import MarketRegime


def test_hard_cap_enforced():
    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile("s1", max_allocation=0.2, min_fitness=0.5)
    ]

    fitness = {
        "s1": CapitalFitness(
            raw_fitness=0.9,
            fragility_penalty=0.0,
            reasons=[],
            is_capital_eligible=True,
        )
    }

    decision = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert decision.allocations["s1"] == 0.2


def test_fragility_penalty_applied():
    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile("s1", max_allocation=0.3, min_fitness=0.5)
    ]

    fitness = {
        "s1": CapitalFitness(
            raw_fitness=0.8,
            fragility_penalty=0.5,  # 50% haircut
            reasons=[],
            is_capital_eligible=True,
        )
    }

    decision = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert decision.allocations["s1"] == 0.15


def test_regime_throttle_applied():
    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile("s1", max_allocation=0.2, min_fitness=0.5)
    ]

    fitness = {
        "s1": CapitalFitness(
            raw_fitness=0.9,
            fragility_penalty=0.0,
            reasons=[],
            is_capital_eligible=True,
        )
    }

    decision = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.CHAOTIC,
    )

    assert decision.allocations["s1"] == 0.04  # 0.2 * 0.2 throttle


def test_below_min_fitness_gets_zero():
    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile("s1", max_allocation=0.2, min_fitness=0.7)
    ]

    fitness = {
        "s1": CapitalFitness(
            raw_fitness=0.6,
            fragility_penalty=0.0,
            reasons=[],
            is_capital_eligible=True,
        )
    }

    decision = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert decision.allocations["s1"] == 0.0


def test_not_capital_eligible_forces_zero():
    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile("s1", max_allocation=0.5, min_fitness=0.1)
    ]

    fitness = {
        "s1": CapitalFitness(
            raw_fitness=0.9,
            fragility_penalty=0.0,
            reasons=[],
            is_capital_eligible=False,
        )
    }

    decision = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert decision.allocations["s1"] == 0.0
