from modules.strategy_allocation.allocator import CapitalAllocator
from modules.strategy_allocation.config import AllocationConfig
from modules.strategy_allocation.contracts import AllocationCandidate


def test_allocation_normalizes_weights():
    allocator = CapitalAllocator(config=AllocationConfig())

    candidates = [
        AllocationCandidate(
            strategy_id="s1",
            symbol="NIFTY",
            health_score=0.9,
            fitness_score=0.8,
            max_drawdown=0.03,
            age_steps=300,
            state="ACTIVE",
        ),
        AllocationCandidate(
            strategy_id="s2",
            symbol="NIFTY",
            health_score=0.85,
            fitness_score=0.7,
            max_drawdown=0.04,
            age_steps=100,
            state="ACTIVE",
        ),
    ]

    result = allocator.allocate(candidates=candidates)

    assert round(sum(result.weights.values()), 6) == 1.0
    assert "s1" in result.weights
    assert "s2" in result.weights


def test_allocation_blocks_unhealthy_and_risky():
    allocator = CapitalAllocator(
        config=AllocationConfig(min_health=0.8, max_drawdown=0.05)
    )

    candidates = [
        AllocationCandidate(
            strategy_id="bad_health",
            symbol="NIFTY",
            health_score=0.6,
            fitness_score=0.9,
            max_drawdown=0.02,
            age_steps=500,
            state="ACTIVE",
        ),
        AllocationCandidate(
            strategy_id="bad_dd",
            symbol="NIFTY",
            health_score=0.9,
            fitness_score=0.9,
            max_drawdown=0.10,
            age_steps=500,
            state="ACTIVE",
        ),
    ]

    result = allocator.allocate(candidates=candidates)

    assert result.weights == {}
    assert "bad_health" in result.reasons
    assert "bad_dd" in result.reasons


def test_longevity_influences_weight():
    allocator = CapitalAllocator(
        config=AllocationConfig(
            health_weight=0.0,
            fitness_weight=0.0,
            longevity_weight=1.0,
            longevity_half_life=100,
        )
    )

    young = AllocationCandidate(
        strategy_id="young",
        symbol="NIFTY",
        health_score=1.0,
        fitness_score=1.0,
        max_drawdown=0.01,
        age_steps=10,
        state="ACTIVE",
    )

    old = AllocationCandidate(
        strategy_id="old",
        symbol="NIFTY",
        health_score=1.0,
        fitness_score=1.0,
        max_drawdown=0.01,
        age_steps=500,
        state="ACTIVE",
    )

    result = allocator.allocate(candidates=[young, old])

    assert result.weights["old"] > result.weights["young"]
