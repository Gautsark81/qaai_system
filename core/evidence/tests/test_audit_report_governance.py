from datetime import datetime, timezone

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.audit_json_report import generate_audit_report_json


def test_audit_report_includes_governance_metadata():
    """
    Phase 12.4A.4-T3

    Invariants:
    - Governance fields are surfaced verbatim
    - No inference or mutation
    - Reviewer and status are preserved
    """

    decision = DecisionEvidence(
        decision_id="DEC-GOV-1",
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime.now(timezone.utc),
        strategy_id="alpha_1",
        alpha_stream=None,
        market_regime="RANGE",
        regime_confidence=0.7,
        drift_detected=False,
        requested_weight=0.4,
        approved_weight=0.3,
        capital_available=1.0,
        ssr=0.75,
        confidence=0.8,
        risk_score=0.2,
        governance_required=True,
        governance_status="APPROVED",
        reviewer="risk_committee",
        rationale="Approved after volatility review",
        factors=(("volatility", 0.18),),
        parent_decision_id=None,
        checksum="chk-gov-1",
    )

    report = generate_audit_report_json(
        system_id="qaai_system",
        evidence=[decision],
    )

    entry = report.decisions[0]

    assert entry.governance_required is True
    assert entry.governance_status == "APPROVED"
    assert entry.reviewer == "risk_committee"
    assert entry.rationale == "Approved after volatility review"
