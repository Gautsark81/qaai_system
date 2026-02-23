from dataclasses import dataclass, field
from datetime import datetime
from typing import List


# ============================================================
# Phase 13 — Capital Throttle Ledger Entry
# ============================================================

@dataclass(frozen=True)
class CapitalThrottleLedgerEntry:
    """
    Immutable throttle ledger entry.
    """

    strategy_id: str
    throttle_level: float
    reason: str
    decision_checksum: str
    governance_id: str
    timestamp: datetime


# ============================================================
# Phase 13 — Capital Throttle Ledger
# ============================================================

class CapitalThrottleLedger:
    """
    Append-only throttle ledger.

    Must be:
    - Deterministic
    - Append-only
    - Expose entries for inspection
    """

    def __init__(self) -> None:
        self._entries: List[CapitalThrottleLedgerEntry] = []

    @property
    def entries(self) -> List[CapitalThrottleLedgerEntry]:
        return list(self._entries)

    def append(self, entry: CapitalThrottleLedgerEntry) -> None:
        self._entries.append(entry)