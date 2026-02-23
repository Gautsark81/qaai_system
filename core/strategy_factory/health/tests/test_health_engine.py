from core.strategy_factory.health.health_engine import StrategyHealthEngine


def test_health_engine_runs():
    engine = StrategyHealthEngine()

    report = engine.evaluate(
        strategy_dna="abc",
        performance_metrics={"sharpe": 1.2},
        risk_metrics={"max_drawdown": 0.2, "volatility": 0.3},
        signal_metrics={"entropy": 0.2, "autocorr": 0.1},
        regime_alignment={"bull": 0.8},
        complexity_penalty=0.1,
    )

    assert report.snapshot.health_score > 0.0
