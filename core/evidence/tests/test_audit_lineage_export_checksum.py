from copy import deepcopy

from core.evidence.audit_timeline import build_audit_timeline
from core.evidence.audit_lineage_graph import build_audit_lineage_graph
from core.evidence.audit_lineage_export import export_lineage_graph_json
from core.evidence.decision_contracts import DecisionEvidence


def _decision(decision_id: str, parent: str | None = None, *, rationale: str = "test"):
    return DecisionEvidence(
        decision_id=decision_id,
        decision_type="CAPITAL_ALLOC",
        timestamp=None,
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
        rationale=rationale,
        factors=(),
        parent_decision_id=parent,
        checksum=f"chk-{decision_id}",
    )


def test_lineage_export_checksum_is_deterministic_and_sensitive():
    """
    Phase 12.5C.1-T4

    Invariants:
    - Same lineage → same checksum
    - Any semantic change → checksum changes
    - No mutation of inputs
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")

    timeline = build_audit_timeline([d1, d2])
    graph = build_audit_lineage_graph(timeline)

    export_1 = export_lineage_graph_json(graph)
    export_2 = export_lineage_graph_json(graph)

    # Deterministic
    assert export_1["checksum"] == export_2["checksum"]

    # --- Mutated semantic content ---
    d2_changed = _decision("D2", parent="D1", rationale="UPDATED")
    timeline_changed = build_audit_timeline([d1, d2_changed])
    graph_changed = build_audit_lineage_graph(timeline_changed)
    export_changed = export_lineage_graph_json(graph_changed)

    # Governance-sensitive
    assert export_1["checksum"] != export_changed["checksum"]
