from core.strategy_factory.health.snapshot import StrategyHealthSnapshot
from core.strategy_factory.health.meta_alpha.cross_strategy_signal import (
    CrossStrategySignal,
)


def test_cross_strategy_signal_uses_existing_health_snapshots():
    snapshots = [
        StrategyHealthSnapshot(
            health_score=0.7,
            confidence=0.8,
            decay_risk=0.1,
            ssr=0.65,
            max_drawdown=0.08,
            total_trades=200,
        ),
        StrategyHealthSnapshot(
            health_score=0.4,
            confidence=0.7,
            decay_risk=0.3,
            ssr=0.45,
            max_drawdown=0.25,
            total_trades=150,
        ),
    ]

    signal = CrossStrategySignal.from_snapshots(
        name="HEALTH_MEAN",
        snapshots=snapshots,
    )

    assert signal.value > 0.0
    assert signal.count == 2
