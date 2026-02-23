from typing import Dict, Any, List, Tuple

from core.evidence.audit_lineage_graph import AuditLineageGraph
from core.evidence.checksum import compute_checksum


def export_lineage_graph_json(
    graph: AuditLineageGraph,
) -> Dict[str, Any]:
    """
    Phase 12.5C

    Deterministic, governance-grade lineage export.

    Invariants:
    - PURE (no mutation, no side effects)
    - Canonical ordering
    - Governance-sensitive checksum
    """

    # ----------------------------
    # Canonical Nodes
    # ----------------------------
    nodes: List[Dict[str, Any]] = []
    for node in sorted(graph.nodes.values(), key=lambda n: n.decision_id):
        nodes.append(
            {
                "decision_id": node.decision_id,
                "decision_type": node.decision_type,
                "strategy_id": node.strategy_id,
                "governance_required": node.governance_required,
                "governance_status": node.governance_status,
                "reviewer": node.reviewer,
                "rationale": node.rationale,
                "checksum": node.checksum,
            }
        )

    # ----------------------------
    # Canonical Edges
    # ----------------------------
    edges: List[Dict[str, str]] = []
    for edge in sorted(
        graph.edges,
        key=lambda e: (e.parent_id, e.child_id),
    ):
        edges.append(
            {
                "parent_id": edge.parent_id,
                "child_id": edge.child_id,
            }
        )

    # ----------------------------
    # Canonical Orphans (STRUCTURED)
    # ----------------------------
    orphans: List[Dict[str, str]] = []
    for orphan in sorted(graph.orphans, key=lambda o: o.decision_id):
        orphans.append(
            {
                "decision_id": orphan.decision_id,
            }
        )

    # ----------------------------
    # Deterministic Checksum
    # ----------------------------
    checksum_fields: List[Tuple[str, Any]] = []

    for n in nodes:
        checksum_fields.append(("node", tuple(n.values())))

    for e in edges:
        checksum_fields.append(("edge", (e["parent_id"], e["child_id"])))

    for o in orphans:
        checksum_fields.append(("orphan", o["decision_id"]))

    export_checksum = compute_checksum(fields=checksum_fields)

    # ----------------------------
    # Final Export
    # ----------------------------
    return {
        "nodes": nodes,
        "edges": edges,
        "orphans": orphans,
        "checksum": export_checksum,
    }
