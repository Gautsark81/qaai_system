from core.strategy_factory.promotion.scaling.live_capital_scaler import (
    LiveCapitalScaler,
)

def test_operator_freeze_blocks_scaling(
    live_strategy_context,
    strong_live_ssr_metrics,
    safe_risk_envelope,
):
    live_strategy_context.operator_veto = True

    scaler = LiveCapitalScaler()

    decision = scaler.evaluate(
        strategy=live_strategy_context,
        ssr_metrics=strong_live_ssr_metrics,
        risk_envelope=safe_risk_envelope,
        current_capital=1_000_000,
    )

    assert decision.allowed is False
    assert "operator" in decision.reason.lower()
