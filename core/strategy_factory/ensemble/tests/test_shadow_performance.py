from core.strategy_factory.ensemble import (
    EnsembleStrategy,
    EnsembleSnapshot,
)
from core.strategy_factory.ensemble.shadow_performance import (
    ShadowPerformanceComparator,
)


def test_shadow_performance_comparator_runs():
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

    strategy_returns = {
        "A": 0.05,
        "B": -0.02,
    }

    result = ShadowPerformanceComparator.compare(
        snap,
        strategy_returns,
    )

    assert isinstance(result.return_delta, float)
    assert isinstance(result.drawdown_delta, float)