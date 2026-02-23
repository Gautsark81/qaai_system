def test_capital_scaling_audit_is_deterministic(
    live_strategy_context,
    strong_live_ssr_metrics,
    safe_risk_envelope,
):
    scaler = LiveCapitalScaler()

    d1 = scaler.evaluate(
        strategy=live_strategy_context,
        ssr_metrics=strong_live_ssr_metrics,
        risk_envelope=safe_risk_envelope,
        current_capital=1_000_000,
    )

    d2 = scaler.evaluate(
        strategy=live_strategy_context,
        ssr_metrics=strong_live_ssr_metrics,
        risk_envelope=safe_risk_envelope,
        current_capital=1_000_000,
    )

    assert d1.audit_event.decision_checksum == d2.audit_event.decision_checksum
