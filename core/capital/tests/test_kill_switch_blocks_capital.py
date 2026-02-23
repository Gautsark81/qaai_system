from core.capital.allocator_v3.allocator import CapitalAllocatorV3
from core.capital.allocator_v3.contracts import StrategyCapitalProfile, CapitalDecisionStatus
from core.strategy_factory.fitness.contracts import FitnessResult
from core.regime.taxonomy import MarketRegime


def test_kill_switch_results_in_blocked_capital_decision():
    """
    HARD INVARIANT:
    When execution is globally disabled, capital allocation
    must not allocate capital (status = BLOCKED).

    Capital allocator itself must NOT raise runtime exceptions.
    """

    allocator = CapitalAllocatorV3()

    profiles = [
        StrategyCapitalProfile(
            strategy_id="s1",
            max_allocation=0.5,
            min_fitness=0.1,
        )
    ]

    fitness = {
        "s1": FitnessResult(
            raw_fitness=0.9,
            fragility_penalty=0.0,
            reasons=["ok"],
            is_capital_eligible=False,  # simulate blocked execution
        )
    }

    decision = allocator.allocate(
        profiles=profiles,
        fitness=fitness,
        regime=MarketRegime.TREND_LOW_VOL,
    )

    assert decision.status == CapitalDecisionStatus.BLOCKED
    assert decision.total_allocated == 0.0
