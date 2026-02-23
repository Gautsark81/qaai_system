from modules.sim.phase13_orchestrator import Phase13SIMOrchestrator
from modules.capital.allocator import CapitalAllocator
from modules.capital.correlation_signal import CorrelationSignal
from modules.execution.portfolio_guard import PortfolioExecutionGuard
from modules.regime.signal import RegimeSignal
from modules.regime.detector import RegimeFeatures


def test_phase13_sim_orchestration_scales_down_safely():
    orchestrator = Phase13SIMOrchestrator(
        capital_allocator=CapitalAllocator(),
        correlation_signal=CorrelationSignal(),
        regime_signal=RegimeSignal(),
        execution_guard=PortfolioExecutionGuard(),
    )

    decision = orchestrator.evaluate(
        equities=[100, 120, 90],
        volatility=0.04,
        cash_ratio=0.2,
        series={
            "A": [1, 2, 3],
            "B": [2, 4, 6],
        },
        weights={"A": 0.7, "B": 0.3},
        regime_features=RegimeFeatures(
            volatility=0.04,
            trend_strength=0.6,
            drawdown_pct=0.10,
        ),
        requested_notional=100_000,
    )

    assert decision.scale_factor <= 1.0
    assert decision.max_notional <= 100_000
    assert "CORR" in decision.reason
    assert "REGIME" in decision.reason
