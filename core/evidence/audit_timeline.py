from dataclasses import dataclass
from typing import Iterable, List, Iterator
from copy import deepcopy

from core.evidence.decision_contracts import DecisionEvidence


# ----------------------------
# Contracts
# ----------------------------

@dataclass(frozen=True)
class AuditTimelineEntry:
    decision_id: str
    decision_type: str
    timestamp: object
    strategy_id: str | None
    parent_decision_id: str | None
    governance_required: bool
    governance_status: str | None
    reviewer: str | None
    rationale: str | None
    checksum: str


@dataclass(frozen=True)
class AuditTimeline:
    """
    Immutable, read-only audit timeline.

    Behaves like a sequence of AuditTimelineEntry
    without exposing mutation.
    """
    entries: List[AuditTimelineEntry]

    # ----------------------------
    # Sequence behavior (READ-ONLY)
    # ----------------------------

    def __iter__(self) -> Iterator[AuditTimelineEntry]:
        return iter(self.entries)

    def __getitem__(self, index: int) -> AuditTimelineEntry:
        return self.entries[index]

    def __len__(self) -> int:
        return len(self.entries)


# ----------------------------
# Builder
# ----------------------------

def build_audit_timeline(
    evidence: Iterable[DecisionEvidence],
) -> AuditTimeline:
    """
    Phase 12.5A.1

    Invariants:
    - Caller-provided ordering is preserved EXACTLY
    - Parent-child lineage is exposed, not inferred
    - Function is PURE (no mutation, no side effects)
    - Deterministic across runs
    """

    # Defensive deep copy to guarantee purity
    evidence_copy = deepcopy(list(evidence))

    entries: List[AuditTimelineEntry] = []

    for e in evidence_copy:
        entries.append(
            AuditTimelineEntry(
                decision_id=e.decision_id,
                decision_type=e.decision_type,
                timestamp=e.timestamp,
                strategy_id=e.strategy_id,
                parent_decision_id=e.parent_decision_id,
                governance_required=e.governance_required,
                governance_status=e.governance_status,
                reviewer=e.reviewer,
                rationale=e.rationale,
                checksum=e.checksum,
            )
        )

    return AuditTimeline(entries=entries)
