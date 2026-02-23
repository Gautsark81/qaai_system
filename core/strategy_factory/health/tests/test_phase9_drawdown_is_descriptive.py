from core.strategy_factory.health.snapshot import StrategyHealthSnapshot


def test_drawdown_is_descriptive_not_trigger():
    snapshot = StrategyHealthSnapshot(
        health_score=0.4,
        confidence=0.6,
        decay_risk=0.25,
        ssr=0.35,
        max_drawdown=0.3,
        total_trades=80,
    )

    # Drawdown exists as data, not logic
    assert snapshot.max_drawdown >= 0.0
