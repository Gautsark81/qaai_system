from core.strategy_factory.promotion.scaling.live_capital_scaler import (
    LiveCapitalScaler,
)


def test_capital_scaling_emits_audit_event(
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

    assert decision.audit_event is not None
    assert decision.audit_event.strategy_id == live_strategy_context.strategy_id
