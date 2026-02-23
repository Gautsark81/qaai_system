from datetime import datetime, timezone

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.audit_timeline import build_audit_timeline


def _decision(decision_id: str, parent: str | None = None) -> DecisionEvidence:
    return DecisionEvidence(
        decision_id=decision_id,
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
        parent_decision_id=parent,
        checksum=f"chk-{decision_id}",
    )


def test_timeline_preserves_decision_order():
    """
    Phase 12.5A.1-T1

    Invariants:
    - Timeline order MUST exactly match input evidence order
    - No sorting
    - No grouping
    - No mutation
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")
    d3 = _decision("D3", parent="D2")

    evidence = [d1, d2, d3]

    timeline = build_audit_timeline(evidence=evidence)

    timeline_ids = [entry.decision_id for entry in timeline.entries]

    assert timeline_ids == ["D1", "D2", "D3"]
