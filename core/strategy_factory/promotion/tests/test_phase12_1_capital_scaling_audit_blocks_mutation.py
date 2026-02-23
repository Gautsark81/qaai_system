import pytest


def test_capital_scaling_audit_event_is_immutable(
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

    audit_event = decision.audit_event

    with pytest.raises(AttributeError):
        audit_event.scale_factor = 99
