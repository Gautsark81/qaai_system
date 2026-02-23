from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ReplayDiscrepancy:
    component: str
    description: str


@dataclass(frozen=True)
class ReplayWarning:
    component: str
    message: str


@dataclass(frozen=True)
class ReplayResult:
    """
    Canonical output of any offline replay.

    This object is:
    - immutable
    - JSON-safe
    - persistable
    - auditor-readable
    """

    replay_id: str
    snapshot_hash: str
    chain_hash: str

    verification_status: bool

    replayed_components: List[str] = field(default_factory=list)
    discrepancies: List[ReplayDiscrepancy] = field(default_factory=list)
    warnings: List[ReplayWarning] = field(default_factory=list)

    audit_summary: Optional[str] = None

    @property
    def is_clean(self) -> bool:
        """
        Strong proof signal:
        - no discrepancies
        - integrity verified
        """
        return self.verification_status and not self.discrepancies