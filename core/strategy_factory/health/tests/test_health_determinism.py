from core.strategy_factory.health.health_engine import StrategyHealthEngine


def test_deterministic_output():
    engine = StrategyHealthEngine()

    r1 = engine.evaluate(
        strategy_dna="d",
        performance_metrics={"sharpe": 1},
        risk_metrics={"max_drawdown": 0.5, "volatility": 0.4},
        signal_metrics={"entropy": 0.3, "autocorr": 0.2},
        regime_alignment={"r": 0.5},
        complexity_penalty=0.2,
    )

    r2 = engine.evaluate(
        strategy_dna="d",
        performance_metrics={"sharpe": 1},
        risk_metrics={"max_drawdown": 0.5, "volatility": 0.4},
        signal_metrics={"entropy": 0.3, "autocorr": 0.2},
        regime_alignment={"r": 0.5},
        complexity_penalty=0.2,
    )

    assert r1.inputs_hash == r2.inputs_hash
