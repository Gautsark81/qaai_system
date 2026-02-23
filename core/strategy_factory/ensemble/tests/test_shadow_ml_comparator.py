from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
)
from core.strategy_factory.ensemble.shadow_ml import (
    ShadowMLComparator,
)


def test_shadow_ml_comparator_runs():
    strategies = [
        EnsembleStrategy("A", 95, 2),
        EnsembleStrategy("B", 85, 10),
    ]

    snap = EnsembleSnapshot(
        strategies,
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
        meta_ml_enabled=True,
    )

    comparison = ShadowMLComparator.compare(snap)

    assert comparison.total_drift >= 0
    assert isinstance(comparison.allocation_drift, dict)