# core/evidence/decision_store.py

from typing import Iterable, List, Optional
from threading import Lock

from core.evidence.decision_contracts import DecisionEvidence


class DecisionEvidenceStore:
    """
    Append-only, lineage-safe store for DecisionEvidence.

    LOCKED INVARIANTS:
    - Append-only (no mutation, no delete)
    - Returned collections are immutable snapshots
    - Parent decision MUST exist before child is appended
    - Thread-safe
    """

    def __init__(self):
        self._records: List[DecisionEvidence] = []
        self._index: dict[str, DecisionEvidence] = {}
        self._lock = Lock()

    # -------------------------------------------------
    # WRITE
    # -------------------------------------------------
    def append(self, evidence: DecisionEvidence) -> None:
        """
        Append evidence to the store.

        Enforces:
        - No orphan decisions
        - No duplicate decision_id
        """
        with self._lock:
            decision_id = evidence.decision_id

            # Defensive: duplicate IDs forbidden
            if decision_id in self._index:
                raise ValueError(f"Duplicate decision_id: {decision_id}")

            # Lineage enforcement
            parent_id = evidence.parent_decision_id
            if parent_id is not None and parent_id not in self._index:
                raise ValueError(
                    f"Parent decision not found: {parent_id}"
                )

            self._records.append(evidence)
            self._index[decision_id] = evidence

    # -------------------------------------------------
    # READ
    # -------------------------------------------------
    def all(self) -> Iterable[DecisionEvidence]:
        """
        Immutable snapshot of all decisions.
        """
        with self._lock:
            return tuple(self._records)

    def get(self, decision_id: str) -> Optional[DecisionEvidence]:
        """
        Retrieve a decision by ID.
        """
        with self._lock:
            return self._index.get(decision_id)

    def by_strategy(self, strategy_id: str) -> Iterable[DecisionEvidence]:
        with self._lock:
            return tuple(
                e for e in self._records
                if e.strategy_id == strategy_id
            )

    def by_type(self, decision_type: str) -> Iterable[DecisionEvidence]:
        with self._lock:
            return tuple(
                e for e in self._records
                if e.decision_type == decision_type
            )


# -------------------------------------------------
# TEST / DEFAULT IN-MEMORY IMPLEMENTATION
# -------------------------------------------------

class InMemoryDecisionStore(DecisionEvidenceStore):
    """
    In-memory decision store for tests and local execution.

    Differences vs DecisionEvidenceStore:
    - all() returns a LIST (test ergonomics)
    - core store remains tuple-based and immutable
    """

    def all(self):
        # Return list for semantic equality checks in tests
        return list(super().all())


__all__ = [
    "DecisionEvidenceStore",
    "InMemoryDecisionStore",
]
