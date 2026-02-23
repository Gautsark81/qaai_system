from datetime import datetime, timezone
import copy

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.audit_json_report import generate_audit_report_json


def _make_decision(decision_id: str) -> DecisionEvidence:
    return DecisionEvidence(
        decision_id=decision_id,
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        strategy_id="alpha_1",
        alpha_stream=None,
        market_regime="TREND",
        regime_confidence=0.92,
        drift_detected=False,
        requested_weight=None,
        approved_weight=0.4,
        capital_available=1.0,
        ssr=0.81,
        confidence=0.88,
        risk_score=None,
        governance_required=False,
        governance_status=None,
        reviewer=None,
        rationale="baseline audit test",
        factors=(("ssr", 0.81),),
        parent_decision_id=None,
        checksum="chk-001",
    )


def test_audit_report_json_baseline_structure_and_determinism():
    """
    Phase 12.4A.4-T1

    Invariants:
    - Audit report generation is deterministic
    - No mutation of input evidence
    - Summary and metadata are correct
    """

    decision = _make_decision("DECISION-1")
    evidence = [decision]

    evidence_snapshot = copy.deepcopy(evidence)

    report_1 = generate_audit_report_json(
        system_id="qaai_system",
        evidence=evidence,
    )

    report_2 = generate_audit_report_json(
        system_id="qaai_system",
        evidence=evidence,
    )

    # --- Structural invariants ---
    assert report_1.system_id == "qaai_system"
    assert report_1.summary.total_decisions == 1
    assert report_1.generated_at.tzinfo is not None

    # --- Determinism ---
    assert report_1 == report_2

    # --- No mutation ---
    assert evidence == evidence_snapshot
