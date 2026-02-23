from core.strategy_factory.health.snapshot import StrategyHealthSnapshot
from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)


def test_cross_strategy_signal_is_deterministic():
    snapshots = [
        StrategyHealthSnapshot(
            health_score=0.6,
            confidence=0.8,
            decay_risk=0.2,
            ssr=0.55,
            max_drawdown=0.15,
            total_trades=100,
        ),
        StrategyHealthSnapshot(
            health_score=0.6,
            confidence=0.8,
            decay_risk=0.2,
            ssr=0.55,
            max_drawdown=0.15,
            total_trades=100,
        ),
    ]

    s1 = CrossStrategySignal.from_snapshots(
        name="HEALTH_MEAN",
        snapshots=snapshots,
    )
    s2 = CrossStrategySignal.from_snapshots(
        name="HEALTH_MEAN",
        snapshots=snapshots,
    )

    assert s1.value == s2.value
