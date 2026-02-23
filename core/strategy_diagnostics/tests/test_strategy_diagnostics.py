import inspect

from core.strategy_diagnostics.health_metrics import StrategyHealthMetrics
from core.strategy_diagnostics.diagnostics import StrategyDiagnosticsEngine
from core.strategy_diagnostics.health_score import StrategyHealthScore
from core.strategy_diagnostics.diagnostic_snapshot import StrategyDiagnosticSnapshot


def test_critical_strategy_health():
    metrics = StrategyHealthMetrics(
        pnl=-5.0,
        drawdown=0.5,
        win_rate=0.3,
    )

    score = StrategyDiagnosticsEngine.evaluate(metrics)

    assert isinstance(score, StrategyHealthScore)
    assert score.status == "CRITICAL"


def test_healthy_strategy_health():
    metrics = StrategyHealthMetrics(
        pnl=10.0,
        drawdown=0.1,
        win_rate=0.6,
    )

    score = StrategyDiagnosticsEngine.evaluate(metrics)

    assert score.status == "HEALTHY"


def test_diagnostic_snapshot_creation():
    score = StrategyHealthScore(score=0.8, status="HEALTHY")

    snapshot = StrategyDiagnosticSnapshot(
        timestamp=1000,
        strategy_id="strategy-1",
        health=score,
        notes="stable regime",
    )

    assert snapshot.strategy_id == "strategy-1"
    assert snapshot.health.status == "HEALTHY"


def test_no_execution_authority():
    modules = [
        StrategyDiagnosticsEngine,
        StrategyDiagnosticSnapshot,
    ]

    forbidden = [
        "execute",
        "order",
        "broker",
        "retry",
        "sleep",
        "while",
        "for ",
        "call(",
    ]

    for obj in modules:
        source = inspect.getsource(obj).lower()
        for word in forbidden:
            assert word not in source
