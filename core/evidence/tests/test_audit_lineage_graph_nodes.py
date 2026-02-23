"""
Phase 12.5B.1-T1

Audit Lineage Graph — Node Preservation

Invariant:
- Every AuditTimeline entry becomes exactly one graph node
- No missing nodes
- No extra nodes
- Node identity is decision_id
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


def test_lineage_graph_preserves_exact_decision_set():
    """
    Phase 12.5B.1-T1

    Invariants:
    - Graph contains exactly one node per timeline entry
    - No missing decision_ids
    - No extra nodes
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")
    d3 = _decision("D3", parent="D2")

    timeline = build_audit_timeline([d1, d2, d3])

    graph = build_audit_lineage_graph(timeline)

    node_ids = {node.decision_id for node in graph.nodes}

    assert node_ids == {"D1", "D2", "D3"}
    assert len(graph.nodes) == 3
