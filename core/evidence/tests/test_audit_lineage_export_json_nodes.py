from core.evidence.audit_lineage_graph import build_audit_lineage_graph
from core.evidence.audit_timeline import build_audit_timeline
from core.evidence.audit_lineage_export import export_lineage_graph_json


def _decision(decision_id, parent=None):
    from datetime import datetime
    from core.evidence.decision_contracts import DecisionEvidence

    return DecisionEvidence(
        decision_id=decision_id,
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime.utcnow(),
        strategy_id="alpha",
        alpha_stream=None,
        market_regime=None,
        regime_confidence=None,
        drift_detected=False,
        requested_weight=None,
        approved_weight=None,
        capital_available=None,
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


def test_json_export_preserves_exact_node_set():
    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")
    d3 = _decision("D3", parent="D2")

    timeline = build_audit_timeline([d1, d2, d3])
    graph = build_audit_lineage_graph(timeline)

    exported = export_lineage_graph_json(graph)

    node_ids = {n["decision_id"] for n in exported["nodes"]}

    assert node_ids == {"D1", "D2", "D3"}
