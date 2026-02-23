from core.strategy_factory.health.snapshot import StrategyHealthSnapshot
from core.strategy_factory.health.meta_alpha.ensemble_summary import EnsembleSummary


def test_ensemble_summary_is_descriptive_only():
    snapshots = [
        StrategyHealthSnapshot(
            health_score=0.62,
            confidence=0.8,
            decay_risk=0.15,
            ssr=0.58,
            max_drawdown=0.12,
            total_trades=240,
        ),
        StrategyHealthSnapshot(
            health_score=0.48,
            confidence=0.7,
            decay_risk=0.25,
            ssr=0.44,
            max_drawdown=0.22,
            total_trades=180,
        ),
    ]

    summary = EnsembleSummary.from_snapshots(snapshots)

    assert summary.count == 2
    assert isinstance(summary.mean_health, float)
    assert isinstance(summary.dispersion, float)
