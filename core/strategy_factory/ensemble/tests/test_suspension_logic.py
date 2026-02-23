from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
    EnsembleAllocator,
)


def test_drawdown_suspension():
    strategies = [
        EnsembleStrategy("SAFE", 90, 5),
        EnsembleStrategy("BREACH", 90, 40),
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

    assert result.allocations["BREACH"] == 0
    assert "BREACH" in result.suspensions