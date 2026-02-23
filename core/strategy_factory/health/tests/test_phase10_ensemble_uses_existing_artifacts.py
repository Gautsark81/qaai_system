from core.strategy_factory.health.snapshot import StrategyHealthSnapshot
from core.strategy_factory.health.meta_alpha.ensemble_summary import EnsembleSummary


def test_ensemble_accepts_only_health_snapshots():
    snapshots = [
        StrategyHealthSnapshot(
            health_score=0.55,
            confidence=0.75,
            decay_risk=0.2,
            ssr=0.5,
            max_drawdown=0.18,
            total_trades=120,
        )
    ]

    summary = EnsembleSummary.from_snapshots(snapshots)

    assert summary.count == 1
