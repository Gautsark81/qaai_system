def test_capital_scaling_audit_links_decision(
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

    assert decision.audit_event.decision_checksum == decision.evidence_checksum
