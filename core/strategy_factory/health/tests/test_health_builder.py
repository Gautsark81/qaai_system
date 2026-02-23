import pytest

from core.strategy_factory.health.health_builder import StrategyHealthBuilder


def test_health_builder_computes_ssr():
    snapshot = StrategyHealthBuilder.build(
        performance_score=0.8,
        risk_score=0.6,
        stability_score=0.7,
    )

    # SSR must be computed and bounded
    assert 0.0 <= snapshot.ssr <= 1.0

    # Component integrity
    assert snapshot.performance_score == 0.8
    assert snapshot.risk_score == 0.6
    assert snapshot.stability_score == 0.7


def test_health_builder_is_deterministic():
    args = dict(
        performance_score=0.7,
        risk_score=0.7,
        stability_score=0.7,
    )

    s1 = StrategyHealthBuilder.build(**args)
    s2 = StrategyHealthBuilder.build(**args)

    assert s1 == s2
