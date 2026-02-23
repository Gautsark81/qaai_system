from core.evidence.audit_lineage_export import export_lineage_graph_json
from core.evidence.audit_timeline import build_audit_timeline
from core.evidence.audit_lineage_graph import build_audit_lineage_graph
from core.evidence.decision_contracts import DecisionEvidence
from datetime import datetime, timezone


def _decision(decision_id: str, parent: str | None = None):
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
        approved_weight=None,
        capital_available=1.0,
        ssr=None,
        confidence=None,
        risk_score=None,
        governance_required=False,
        governance_status=None,
        reviewer=None,
        rationale="test",
        factors=(),
        parent_decision_id=parent,
        checksum=f"chk-{decision_id}",
    )


def test_export_includes_orphan_decisions_explicitly():
    """
    Phase 12.5C.1-T3

    Invariants:
    - Orphan decisions are NOT dropped
    - Orphans are explicitly surfaced in export
    - Export remains deterministic and pure
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="MISSING_PARENT")

    timeline = build_audit_timeline([d1, d2])
    graph = build_audit_lineage_graph(timeline)

    exported = export_lineage_graph_json(graph)

    # --- Nodes ---
    node_ids = {n["decision_id"] for n in exported["nodes"]}
    assert node_ids == {"D1", "D2"}

    # --- Orphans ---
    orphan_ids = {o["decision_id"] for o in exported["orphans"]}
    assert orphan_ids == {"D2"}

    # --- Edges ---
    edges = exported["edges"]
    assert edges == []  # No valid parent → child edge possible
