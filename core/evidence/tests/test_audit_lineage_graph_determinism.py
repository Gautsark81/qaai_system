"""
Phase 12.5B.1-T5

Audit Lineage Graph — Deterministic Fingerprint

Invariants:
- Same timeline input → identical lineage graph fingerprint
- Fingerprint changes if lineage semantics change
- No dependency on object identity or runtime ordering
"""

from datetime import datetime, timezone

from core.evidence.audit_timeline import build_audit_timeline
from core.evidence.audit_lineage_graph import (
    build_audit_lineage_graph,
    compute_lineage_graph_fingerprint,
)
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


def test_lineage_graph_fingerprint_is_deterministic():
    """
    Phase 12.5B.1-T5

    Invariants:
    - Identical lineage → identical fingerprint
    - Independent runs produce same result
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")
    d3 = _decision("D3", parent="D2")

    evidence = [d1, d2, d3]
    timeline = build_audit_timeline(evidence)

    graph_1 = build_audit_lineage_graph(timeline)
    graph_2 = build_audit_lineage_graph(timeline)

    fp_1 = compute_lineage_graph_fingerprint(graph_1)
    fp_2 = compute_lineage_graph_fingerprint(graph_2)

    assert fp_1 == fp_2
    assert isinstance(fp_1, str)
    assert len(fp_1) >= 32  # cryptographic-grade


def test_lineage_graph_fingerprint_changes_on_semantic_change():
    """
    Phase 12.5B.1-T5

    Invariant:
    - Any semantic lineage change MUST alter fingerprint
    """

    # Original lineage
    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")

    timeline_1 = build_audit_timeline([d1, d2])
    graph_1 = build_audit_lineage_graph(timeline_1)
    fp_1 = compute_lineage_graph_fingerprint(graph_1)

    # Modified lineage (parent changed)
    d2_alt = _decision("D2", parent=None)
    timeline_2 = build_audit_timeline([d1, d2_alt])
    graph_2 = build_audit_lineage_graph(timeline_2)
    fp_2 = compute_lineage_graph_fingerprint(graph_2)

    assert fp_1 != fp_2
