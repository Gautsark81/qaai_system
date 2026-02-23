from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
    EnsembleAllocator,
)


def test_deterministic_allocation():
    strategies = [
        EnsembleStrategy("A", 90),
        EnsembleStrategy("B", 85),
        EnsembleStrategy("C", 80),
    ]

    snap = EnsembleSnapshot(strategies, 600, 600, 600, 600)

    result1 = EnsembleAllocator.allocate(snap)
    result2 = EnsembleAllocator.allocate(snap)

    assert result1.allocations == result2.allocations


def test_governance_caps_enforced():
    strategies = [
        EnsembleStrategy("A", 90),
        EnsembleStrategy("B", 90),
    ]

    snap = EnsembleSnapshot(strategies, 1000, 500, 300, 300)

    result = EnsembleAllocator.allocate(snap)

    assert sum(result.allocations.values()) <= 500
    for v in result.allocations.values():
        assert v <= 300