from core.strategy_factory.promotion.scaling.live_capital_scaler import (
    LiveCapitalScaler,
)

def test_capital_scaling_is_reversible(
    live_strategy_context,
    strong_live_ssr_metrics,
    unsafe_risk_envelope,
):
    scaler = LiveCapitalScaler()

    decision = scaler.evaluate(
        strategy=live_strategy_context,
        ssr_metrics=strong_live_ssr_metrics,
        risk_envelope=unsafe_risk_envelope,
        current_capital=2_000_000,
    )

    assert decision.allowed is False
    assert decision.scale_factor <= 1.0
