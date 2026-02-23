from core.strategy_factory.promotion.scaling.live_capital_scaler import (
    LiveCapitalScaler,
)
from core.strategy_factory.promotion.state_machine.promotion_state import PromotionState

def test_live_capital_scaling_happy_path(
    live_strategy_context,
    strong_live_ssr_metrics,
    safe_risk_envelope,
):
    scaler = LiveCapitalScaler()

    decision = scaler.evaluate(
        strategy=live_strategy_context,
        ssr_metrics=strong_live_ssr_metrics,
        risk_envelope=safe_risk_envelope,
        current_capital=1_000_000,
    )

    assert decision.allowed is True
    assert decision.scale_factor > 1.0
    assert decision.scale_factor <= 1.25  # capped growth
