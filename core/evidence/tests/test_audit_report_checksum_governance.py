import copy
from datetime import datetime, timezone

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.audit_json_report import generate_audit_report_json


def _decision(**overrides):
    base = dict(
        decision_id="DEC-1",
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
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
        rationale="Approved after review",
        factors=(("volatility", 0.18),),
        parent_decision_id=None,
        checksum="chk-1",
    )
    base.update(overrides)
    return DecisionEvidence(**base)


def test_audit_checksum_changes_when_governance_changes():
    """
    Phase 12.4A.4-T4

    Invariant:
    - Audit report checksum must change if governance metadata changes
    """

    d1 = _decision()
    d2 = _decision(rationale="Approved after SECOND review")

    report_1 = generate_audit_report_json(
        system_id="qaai_system",
        evidence=[d1],
    )

    report_2 = generate_audit_report_json(
        system_id="qaai_system",
        evidence=[d2],
    )

    assert report_1.checksum != report_2.checksum
