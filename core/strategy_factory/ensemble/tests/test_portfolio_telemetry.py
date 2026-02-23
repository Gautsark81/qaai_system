from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
    EnsembleAllocator,
)
from core.strategy_factory.ensemble.telemetry import (
    PortfolioTelemetryCalculator,
)


def test_portfolio_telemetry_basic_metrics():
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

    telemetry = PortfolioTelemetryCalculator.calculate(snap, result)

    assert telemetry.total_capital == 1000
    assert telemetry.deployed_capital == 1000
    assert telemetry.suspended_capital == 0
    assert telemetry.suspended_strategy_count == 1
    assert telemetry.active_strategy_count == 1