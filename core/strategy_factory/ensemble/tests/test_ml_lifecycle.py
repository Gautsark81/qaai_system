from core.strategy_factory.ensemble import (
    EnsembleSnapshot,
)
from core.strategy_factory.ensemble.ml_lifecycle import (
    MLLifecycleManager,
)
from core.strategy_factory.ensemble.shadow_performance import (
    ShadowPerformanceResult,
)


def test_ml_lifecycle_manager_runs():
    snap = EnsembleSnapshot(
        strategies=[],
        available_capital=1000,
        global_cap=1000,
        per_strategy_cap=1000,
        concentration_cap=1000,
    )

    history = [
        ShadowPerformanceResult(
            baseline_return=0.01,
            ml_return=0.015,
            return_delta=0.005,
            baseline_drawdown_proxy=0.01,
            ml_drawdown_proxy=0.009,
            drawdown_delta=-0.001,
        )
        for _ in range(20)
    ]

    status = MLLifecycleManager.evaluate(snap, history)

    assert status.promotion_status in {"PROMOTE", "ADVISORY", "DEMOTE"}