from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
    EnsembleAllocator,
)


def test_suspended_capital_redistributed():
    strategies = [
        EnsembleStrategy("A", 90, 0),
        EnsembleStrategy("B", 90, 40),  # suspended
    ]

    snap = EnsembleSnapshot(
        strategies,
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
        suspension_drawdown_pct=30,
        suspension_min_ssr=80,
    )

    result = EnsembleAllocator.allocate(snap)

    assert result.allocations["A"] == 1000
    assert result.allocations["B"] == 0