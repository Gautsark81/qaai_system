from core.strategy_factory.health.health_engine import StrategyHealthEngine


def test_bounds_enforced():
    engine = StrategyHealthEngine()

    report = engine.evaluate(
        strategy_dna="x",
        performance_metrics={"sharpe": 10},
        risk_metrics={"max_drawdown": 0.0, "volatility": 0.0},
        signal_metrics={"entropy": 0.0, "autocorr": 0.0},
        regime_alignment={"any": 1.0},
        complexity_penalty=0.0,
    )

    assert 0.0 <= report.snapshot.health_score <= 1.0
