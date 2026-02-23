from core.strategy_factory.health.snapshot import StrategyHealthSnapshot


def test_performance_summary_fields_exist_and_are_descriptive():
    snapshot = StrategyHealthSnapshot(
        health_score=0.62,
        confidence=0.8,
        decay_risk=0.15,
        ssr=0.58,
        max_drawdown=0.12,
        total_trades=240,
    )

    # Performance intelligence must be readable, not actionable
    assert isinstance(snapshot.health_score, float)
    assert isinstance(snapshot.max_drawdown, float)
    assert isinstance(snapshot.total_trades, int)
