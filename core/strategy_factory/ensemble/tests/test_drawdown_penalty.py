from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
    EnsembleAllocator,
)


def test_drawdown_penalty_reduces_weight():
    strategies = [
        EnsembleStrategy("LOW_DD", 90, 2),   # multiplier 1.0
        EnsembleStrategy("HIGH_DD", 90, 25), # multiplier 0.25
    ]

    snap = EnsembleSnapshot(strategies, 1000, 1000, 1000, 1000)
    result = EnsembleAllocator.allocate(snap)

    assert result.allocations["LOW_DD"] > result.allocations["HIGH_DD"]