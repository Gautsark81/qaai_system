import pytest
from core.strategy_factory.promotion.scaling.live_capital_scaler import LiveCapitalScaler


def test_scaling_requires_governance_chain(
    live_strategy_context,
    strong_live_ssr_metrics,
    safe_risk_envelope,
):
    scaler = LiveCapitalScaler()

    with pytest.raises(ValueError):
        scaler.evaluate(
            strategy=live_strategy_context,
            ssr_metrics=strong_live_ssr_metrics,
            risk_envelope=safe_risk_envelope,
            current_capital=1_000_000,
            governance_chain_id=None,
        )


def test_governance_chain_embedded_in_audit(
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
        governance_chain_id="CHAIN-ABC",
    )

    assert decision.governance_chain_id == "CHAIN-ABC"
    assert decision.audit_event.governance_chain_id == "CHAIN-ABC"


def test_governance_chain_changes_checksum(
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
        governance_chain_id="CHAIN-1",
    )

    d2 = scaler.evaluate(
        strategy=live_strategy_context,
        ssr_metrics=strong_live_ssr_metrics,
        risk_envelope=safe_risk_envelope,
        current_capital=1_000_000,
        governance_chain_id="CHAIN-2",
    )

    assert d1.decision_checksum != d2.decision_checksum