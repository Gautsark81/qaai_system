from datetime import datetime, timezone

import pytest

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.audit_timeline import build_audit_timeline


def _decision(
    decision_id: str,
    *,
    parent: str | None = None,
):
    return DecisionEvidence(
        decision_id=decision_id,
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime.now(timezone.utc),
        strategy_id="alpha_1",
        alpha_stream=None,
        market_regime=None,
        regime_confidence=None,
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
        factors=(),
        parent_decision_id=parent,
        checksum=f"chk-{decision_id}",
    )


def test_audit_timeline_exposes_lineage_without_reordering():
    """
    Phase 12.5A.1-T2

    Invariants:
    - Timeline order matches input order exactly
    - Parent-child lineage is exposed
    - No sorting or inference is applied
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")
    d3 = _decision("D3", parent="D2")

    evidence = [d1, d2, d3]

    timeline = build_audit_timeline(evidence)

    # Order must be preserved
    assert [e.decision_id for e in timeline] == ["D1", "D2", "D3"]

    # Lineage must be visible but untouched
    assert timeline[0].parent_decision_id is None
    assert timeline[1].parent_decision_id == "D1"
    assert timeline[2].parent_decision_id == "D2"
