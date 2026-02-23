from core.strategy_factory.health.health_builder import StrategyHealthBuilder
from core.strategy_factory.health.snapshot import StrategyHealthSnapshot


def test_health_builder_builds_ssr_snapshot():
    snapshot = StrategyHealthBuilder.build(
        performance_score=0.7,
        risk_score=0.8,
        stability_score=0.9,
    )

    assert isinstance(snapshot, StrategyHealthSnapshot)
    assert 0.0 <= snapshot.ssr <= 1.0
    assert snapshot.ssr_components["performance"] == 0.7
