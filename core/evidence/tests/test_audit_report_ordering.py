from datetime import datetime, timezone

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.audit_json_report import generate_audit_report_json


def _decision(decision_id: str, parent: str | None = None):
    return DecisionEvidence(
        decision_id=decision_id,
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
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
        rationale=f"decision {decision_id}",
        factors=(("ssr", 0.8),),
        parent_decision_id=parent,
        checksum=f"chk-{decision_id}",
    )


def test_audit_report_preserves_decision_order_and_lineage():
    """
    Phase 12.4A.4-T2

    Invariants:
    - Decision ordering is preserved
    - Parent-child lineage is retained
    - No implicit sorting or mutation
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")
    d3 = _decision("D3", parent="D2")

    evidence = [d1, d2, d3]

    report = generate_audit_report_json(
        system_id="qaai_system",
        evidence=evidence,
    )

    # Ordered decisions live on the report, not the summary
    decision_ids = [entry.decision_id for entry in report.decisions]
    assert decision_ids == ["D1", "D2", "D3"]

    lineage = {
        entry.decision_id: entry.parent_decision_id
        for entry in report.decisions
    }

    assert lineage["D1"] is None
    assert lineage["D2"] == "D1"
    assert lineage["D3"] == "D2"
