from datetime import datetime, timezone

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.audit_json_report import generate_audit_report_json


def test_audit_report_json_generation():
    e = DecisionEvidence(
        decision_id="d1",
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime.now(timezone.utc),
        strategy_id="alpha_1",
        alpha_stream=None,
        market_regime="TREND",
        regime_confidence=0.9,
        drift_detected=False,
        requested_weight=None,
        approved_weight=0.5,
        capital_available=1.0,
        ssr=0.8,
        confidence=0.9,
        risk_score=None,
        governance_required=False,
        governance_status=None,
        reviewer=None,
        rationale="test",
        factors=(("ssr", 0.8),),
        parent_decision_id=None,
        checksum="chk-1",
    )

    report = generate_audit_report_json(
        system_id="qaai_system",
        evidence=[e],
    )

    assert report.summary.total_decisions == 1
    assert report.system_id == "qaai_system"
