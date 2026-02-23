"""
Phase 12.5B.1-T3

Audit Lineage Graph — Orphan Handling

Invariant:
- Decisions referencing a missing parent MUST be flagged
- Graph construction must not silently drop or infer parents
- Orphan nodes are explicitly exposed
"""

from datetime import datetime, timezone
import pytest

from core.evidence.audit_timeline import build_audit_timeline
from core.evidence.audit_lineage_graph import build_audit_lineage_graph
from core.evidence.decision_contracts import DecisionEvidence


def _decision(
    decision_id: str,
    *,
    parent: str | None = None,
) -> DecisionEvidence:
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


def test_lineage_graph_detects_orphan_decisions():
    """
    Phase 12.5B.1-T3

    Invariants:
    - Missing parent references are NOT ignored
    - Orphan decisions are explicitly reported
    - Graph construction remains deterministic
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="MISSING_PARENT")

    timeline = build_audit_timeline([d1, d2])
    graph = build_audit_lineage_graph(timeline)

    orphan_ids = {o.decision_id for o in graph.orphans}

    assert orphan_ids == {"D2"}
