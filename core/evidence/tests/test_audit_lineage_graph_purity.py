"""
Phase 12.5B.1-T4

Audit Lineage Graph — Purity & Read-Only Guarantees

Invariants:
- Lineage graph construction is PURE
- Input timeline is never mutated
- Graph nodes are independent objects
- No side effects, no enrichment, no inference
"""

from datetime import datetime, timezone
import copy

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


def test_lineage_graph_is_pure_and_non_mutating():
    """
    Phase 12.5B.1-T4

    Invariants:
    - Input timeline remains unchanged
    - Graph does not reuse timeline objects
    - Graph is safe for repeated reads
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")

    evidence = [d1, d2]
    timeline = build_audit_timeline(evidence)

    # Deep copy to detect mutation
    timeline_snapshot = copy.deepcopy(timeline)

    graph = build_audit_lineage_graph(timeline)

    # Timeline must remain unchanged
    assert timeline == timeline_snapshot

    # Graph must not reuse timeline entries
    for node in graph.nodes.values():
        for entry in timeline.entries:
            assert node is not entry

    # Graph must be safely reusable
    graph_again = build_audit_lineage_graph(timeline)
    assert graph == graph_again
