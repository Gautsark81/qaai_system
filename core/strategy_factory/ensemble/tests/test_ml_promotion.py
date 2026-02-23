from core.strategy_factory.ensemble import EnsembleSnapshot
from core.strategy_factory.ensemble.ml_promotion import (
    MLPromotionEngine,
)
from core.strategy_factory.ensemble.shadow_performance import (
    ShadowPerformanceResult,
)


def test_ml_promotion_promotes_when_threshold_met():
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
            ml_return=0.02,
            return_delta=0.01,
            baseline_drawdown_proxy=0.01,
            ml_drawdown_proxy=0.009,
            drawdown_delta=-0.001,
        )
        for _ in range(20)
    ]

    decision = MLPromotionEngine.evaluate(snap, history)

    assert decision.status == "PROMOTE"