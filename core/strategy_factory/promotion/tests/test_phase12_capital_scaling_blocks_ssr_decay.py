from core.strategy_factory.promotion.scaling.live_capital_scaler import (
    LiveCapitalScaler,
)

def test_capital_scaling_blocks_on_ssr_decay(
    live_strategy_context,
    weak_live_ssr_metrics,
    safe_risk_envelope,
):
    scaler = LiveCapitalScaler()

    decision = scaler.evaluate(
        strategy=live_strategy_context,
        ssr_metrics=weak_live_ssr_metrics,
        risk_envelope=safe_risk_envelope,
        current_capital=1_000_000,
    )

    assert decision.allowed is False
    assert "ssr" in decision.reason.lower()
