"""
Phase 12.5B.1-T2

Audit Lineage Graph — Parent → Child Edges

Invariant:
- Parent-child relationships are represented as directed edges
- Edges reflect ONLY explicit parent_decision_id
- No inferred or reordered relationships
"""

from datetime import datetime, timezone

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


def test_lineage_graph_creates_correct_parent_child_edges():
    """
    Phase 12.5B.1-T2

    Invariants:
    - Each parent_decision_id becomes exactly one directed edge
    - Edge direction: parent → child
    - No extra edges
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")
    d3 = _decision("D3", parent="D2")

    timeline = build_audit_timeline([d1, d2, d3])
    graph = build_audit_lineage_graph(timeline)

    edges = {(e.parent_id, e.child_id) for e in graph.edges}

    assert edges == {
        ("D1", "D2"),
        ("D2", "D3"),
    }
