import copy
from datetime import datetime, timezone

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.audit_json_report import generate_audit_report_json


def _make_decision(
    decision_id="DEC-1",
    rationale="Approved after review",
):
    return DecisionEvidence(
        decision_id=decision_id,
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        strategy_id="alpha_1",
        alpha_stream=None,
        market_regime="RANGE",
        regime_confidence=0.8,
        drift_detected=False,
        requested_weight=0.5,
        approved_weight=0.4,
        capital_available=1.0,
        ssr=0.75,
        confidence=0.85,
        risk_score=0.2,
        governance_required=True,
        governance_status="APPROVED",
        reviewer="risk_committee",
        rationale=rationale,
        factors=(("volatility", 0.2),),
        parent_decision_id=None,
        checksum="chk-1",
    )


def test_audit_report_checksum_is_semantically_deterministic():
    """
    Phase 12.4A.4-T5

    Invariants:
    - Identical semantic evidence produces identical audit checksum
    - Object identity, instance recreation, and copying do NOT affect checksum
    """

    d1 = _make_decision()
    d2 = _make_decision()  # fresh instance, same semantics

    # Defensive copies
    d1_copy = copy.deepcopy(d1)
    d2_copy = copy.deepcopy(d2)

    report_1 = generate_audit_report_json(
        system_id="qaai_system",
        evidence=[d1],
    )

    report_2 = generate_audit_report_json(
        system_id="qaai_system",
        evidence=[d2],
    )

    report_3 = generate_audit_report_json(
        system_id="qaai_system",
        evidence=[d1_copy],
    )

    report_4 = generate_audit_report_json(
        system_id="qaai_system",
        evidence=[d2_copy],
    )

    assert report_1.checksum == report_2.checksum
    assert report_2.checksum == report_3.checksum
    assert report_3.checksum == report_4.checksum
