import copy

from core.evidence.audit_timeline import build_audit_timeline
from core.evidence.audit_lineage_graph import build_audit_lineage_graph
from core.evidence.audit_lineage_export import export_lineage_graph_json
from core.evidence.audit_signature import sign_lineage_export


def _decision(decision_id, parent=None):
    from core.evidence.decision_contracts import DecisionEvidence
    from datetime import datetime

    return DecisionEvidence(
        decision_id=decision_id,
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime.utcnow(),
        strategy_id=None,
        parent_decision_id=parent,
        governance_required=False,
        governance_status=None,
        reviewer=None,
        rationale="test",
        checksum=f"chk-{decision_id}",
    )


def test_lineage_signature_is_deterministic_across_runs():
    """
    Phase 12.5C.2-T2

    Invariants:
    - Same lineage export → same signature
    - Timestamp does NOT affect signature
    - Signature binds ONLY to checksum
    - No mutation of inputs
    """

    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")

    timeline = build_audit_timeline([d1, d2])
    graph = build_audit_lineage_graph(timeline)
    exported = export_lineage_graph_json(graph)

    exported_snapshot = copy.deepcopy(exported)

    sig_1 = sign_lineage_export(
        exported,
        signer_id="unit-test-signer",
        secret_key="test-secret",
    )

    sig_2 = sign_lineage_export(
        exported,
        signer_id="unit-test-signer",
        secret_key="test-secret",
    )

    # --- Determinism ---
    assert sig_1["signature"] == sig_2["signature"]
    assert sig_1["algorithm"] == sig_2["algorithm"]
    assert sig_1["signer_id"] == sig_2["signer_id"]
    assert sig_1["checksum"] == sig_2["checksum"]

    # --- Timestamp allowed to differ ---
    assert sig_1["timestamp"] != sig_2["timestamp"]

    # --- Purity ---
    assert exported == exported_snapshot
