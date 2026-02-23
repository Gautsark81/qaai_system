from core.strategy_factory.health.snapshot import StrategyHealthSnapshot


def test_performance_intelligence_has_no_ranking_methods():
    snapshot = StrategyHealthSnapshot(
        health_score=0.5,
        confidence=0.7,
        decay_risk=0.3,
        ssr=0.4,
        max_drawdown=0.2,
        total_trades=100,
    )

    forbidden = [
        "rank",
        "compare",
        "select",
        "optimize",
        "allocate",
    ]

    for attr in forbidden:
        assert not hasattr(snapshot, attr)
