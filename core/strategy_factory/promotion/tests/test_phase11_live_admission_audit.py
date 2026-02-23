from datetime import datetime, timezone

from core.strategy_factory.promotion.admission.live_admission_gate import (
    LiveAdmissionGate,
)

FIXED_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_live_admission_emits_audit_evidence(
    eligible_governed_live_strategy,
    governed_live_ssr_metrics,
    valid_governed_live_risk_envelope,
):
    gate = LiveAdmissionGate()

    decision = gate.evaluate(
        strategy=eligible_governed_live_strategy,
        ssr_metrics=governed_live_ssr_metrics,
        risk_envelope=valid_governed_live_risk_envelope,
        now=FIXED_NOW,
    )

    assert decision.evidence_checksum is not None
    assert decision.timestamp == FIXED_NOW