from core.strategy_factory.health.health_engine import StrategyHealthEngine
from core.strategy_factory.health.artifacts import HealthReport


def test_health_engine_evaluates_to_health_report():
    engine = StrategyHealthEngine()

    report = engine.evaluate(
        strategy_dna="DNA_001",
        performance_metrics={"sharpe": 1.2},
        risk_metrics={"max_drawdown": 0.1, "volatility": 0.2},
        signal_metrics={"entropy": 0.3, "autocorr": 0.1},
        regime_alignment={"bull": 1.0},
        complexity_penalty=0.2,
        learning_registry=None,
    )

    assert isinstance(report, HealthReport)
    assert report.snapshot is not None
    assert 0.0 <= report.snapshot.health_score <= 1.0
