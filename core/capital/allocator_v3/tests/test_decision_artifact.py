from core.capital.allocator_v3.allocator import CapitalAllocatorV3
from core.capital.allocator_v3.contracts import StrategyCapitalProfile
from core.capital.contracts.fitness import CapitalFitness
from core.regime.taxonomy import MarketRegime


def test_decision_contains_full_artifact():
    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile("s1", max_allocation=0.3, min_fitness=0.2)
    ]

    fitness = {
        "s1": CapitalFitness(
            raw_fitness=0.8,
            fragility_penalty=0.25,
            reasons=["stable", "low-drawdown"],
            is_capital_eligible=True,
        )
    }

    decision = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    artifact = decision.decisions["s1"]

    assert artifact.strategy_id == "s1"
    assert artifact.raw_fitness == 0.8
    assert artifact.fragility_penalty == 0.25
    assert artifact.final_allocation == 0.225
    assert artifact.regime == MarketRegime.TREND_LOW_VOL
    assert artifact.reasons == ["stable", "low-drawdown"]
