from datetime import datetime, timezone

from core.evidence.audit_timeline import build_audit_timeline
from core.evidence.audit_lineage_graph import build_audit_lineage_graph
from core.evidence.audit_lineage_export import export_lineage_graph_json
from core.evidence.audit_signature import sign_lineage_export


def _decision(decision_id: str, parent: str | None = None):
    from core.evidence.decision_contracts import DecisionEvidence

    return DecisionEvidence(
        decision_id=decision_id,
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime.now(timezone.utc),
        strategy_id="alpha_1",
        alpha_stream=None,
        market_regime="TREND",
        regime_confidence=0.9,
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
        factors=(("ssr", 0.8),),
        parent_decision_id=parent,
        checksum=f"chk-{decision_id}",
    )


def test_lineage_export_includes_signature_block():
    """
    Phase 12.5C.2-T1

    Invariants:
    - Signed lineage export includes a top-level signature block
    - Signature metadata is explicit and complete
    - Export structure is not mutated
    """

    # --- Build lineage ---
    d1 = _decision("D1")
    d2 = _decision("D2", parent="D1")

    timeline = build_audit_timeline([d1, d2])
    graph = build_audit_lineage_graph(timeline)

    unsigned_export = export_lineage_graph_json(graph)

    signed_export = sign_lineage_export(
        export=unsigned_export,
        signer_id="qaai-system",
        secret_key=b"test-secret-key",
    )

    # --- Signature block must exist ---
    assert "signature" in signed_export

    signature = signed_export["signature"]

    # --- Required signature fields ---
    assert signature["algorithm"] == "HMAC-SHA256"
    assert signature["signer_id"] == "qaai-system"
    assert signature["checksum"] == signed_export["checksum"]
    assert isinstance(signature["signature"], str)
    assert isinstance(signature["signed_at"], str)

    # --- Timestamp must be ISO-8601 UTC ---
    parsed = datetime.fromisoformat(signature["signed_at"])
    assert parsed.tzinfo is not None
