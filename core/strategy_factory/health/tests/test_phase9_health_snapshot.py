import pytest

from core.strategy_factory.health.snapshot import StrategyHealthSnapshot


def test_strategy_health_snapshot_validates_bounds():
    snapshot = StrategyHealthSnapshot(
        health_score=0.5,
        confidence=0.8,
        decay_risk=0.2,
        ssr=0.6,
        max_drawdown=0.1,
        total_trades=100,
    )

    snapshot.validate()  # should not raise


def test_strategy_health_snapshot_rejects_invalid_health_score():
    snapshot = StrategyHealthSnapshot(
        health_score=1.5,  # invalid
        confidence=0.5,
        decay_risk=0.2,
        ssr=0.4,
    )

    with pytest.raises(ValueError):
        snapshot.validate()
