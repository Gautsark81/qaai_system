from core.capital.allocator_v3.allocator import CapitalAllocatorV3
from core.capital.allocator_v3.contracts import StrategyCapitalProfile
from core.strategy_factory.fitness.contracts import CapitalFitness
from core.regime.taxonomy import MarketRegime


def test_capital_attribution_emitted_per_strategy():
    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile("s1", max_allocation=0.4, min_fitness=0.2)
    ]

    fitness = {
        "s1": CapitalFitness(
            raw_fitness=0.9,
            fragility_penalty=0.25,
            reasons=["stable"],
            is_capital_eligible=True,
        )
    }

    decision = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert "s1" in decision.attribution

    attr = decision.attribution["s1"]
    assert attr.strategy_id == "s1"
    assert attr.final_allocation > 0.0
    assert "fragility_penalty" in attr.applied_constraints


def test_capital_attribution_is_deterministic():
    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile("s1", max_allocation=0.3, min_fitness=0.1)
    ]

    fitness = {
        "s1": CapitalFitness(
            raw_fitness=0.8,
            fragility_penalty=0.1,
            reasons=["ok"],
            is_capital_eligible=True,
        )
    }

    d1 = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    d2 = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert d1.attribution == d2.attribution
