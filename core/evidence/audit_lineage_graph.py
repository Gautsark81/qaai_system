from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List
from copy import deepcopy
import hashlib

from core.evidence.audit_timeline import AuditTimeline


# ============================================================
# Internal helpers
# ============================================================

class _NodeMap(dict):
    """
    Dict[str, AuditLineageNode] that ITERATES OVER VALUES.

    Required to satisfy:
    - for node in graph.nodes
    - graph.nodes.values()
    """

    def __iter__(self):
        return iter(self.values())


# ============================================================
# Contracts
# ============================================================

@dataclass(frozen=True)
class AuditLineageNode:
    decision_id: str
    decision_type: str
    timestamp: object
    strategy_id: str | None
    governance_required: bool
    governance_status: str | None
    reviewer: str | None
    rationale: str | None
    checksum: str


@dataclass(frozen=True)
class AuditLineageEdge:
    parent_id: str
    child_id: str


@dataclass(frozen=True)
class AuditLineageGraph:
    nodes: _NodeMap
    edges: List[AuditLineageEdge]
    orphans: List[AuditLineageNode]


# ============================================================
# Builder
# ============================================================

def build_audit_lineage_graph(
    timeline: AuditTimeline,
) -> AuditLineageGraph:
    """
    Phase 12.5B

    Invariants:
    - PURE (no mutation)
    - Deterministic
    - Caller ordering preserved
    - Orphans explicitly surfaced (not raised)
    """

    timeline_copy = deepcopy(timeline)

    nodes = _NodeMap()
    edges: List[AuditLineageEdge] = []
    orphans: List[AuditLineageNode] = []

    # ----------------------------
    # Nodes
    # ----------------------------
    for entry in timeline_copy.entries:
        node = AuditLineageNode(
            decision_id=entry.decision_id,
            decision_type=entry.decision_type,
            timestamp=entry.timestamp,
            strategy_id=entry.strategy_id,
            governance_required=entry.governance_required,
            governance_status=entry.governance_status,
            reviewer=entry.reviewer,
            rationale=entry.rationale,
            checksum=entry.checksum,
        )
        nodes[entry.decision_id] = node

    # ----------------------------
    # Edges + Orphans
    # ----------------------------
    for entry in timeline_copy.entries:
        if entry.parent_decision_id is None:
            continue

        if entry.parent_decision_id not in nodes:
            orphans.append(nodes[entry.decision_id])
            continue

        edges.append(
            AuditLineageEdge(
                parent_id=entry.parent_decision_id,
                child_id=entry.decision_id,
            )
        )

    return AuditLineageGraph(
        nodes=nodes,
        edges=edges,
        orphans=orphans,
    )


# ============================================================
# Deterministic fingerprint
# ============================================================

def compute_lineage_graph_fingerprint(
    graph: AuditLineageGraph,
    *,
    algorithm: str = "sha256",
) -> str:
    """
    Phase 12.5B.1-T5

    Stable semantic fingerprint of lineage graph.
    """

    h = hashlib.new(algorithm)

    for node in sorted(graph.nodes, key=lambda n: n.decision_id):
        for v in (
            node.decision_id,
            node.decision_type,
            str(node.timestamp),
            node.strategy_id,
            node.governance_required,
            node.governance_status,
            node.reviewer,
            node.rationale,
            node.checksum,
        ):
            h.update(repr(v).encode())

    for edge in sorted(
        graph.edges,
        key=lambda e: (e.parent_id, e.child_id),
    ):
        h.update(edge.parent_id.encode())
        h.update(edge.child_id.encode())

    for orphan in sorted(graph.orphans, key=lambda o: o.decision_id):
        h.update(orphan.decision_id.encode())

    return h.hexdigest()
