from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


# ---------------------------------------------------------------------
# Immutable Ledger Entry
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class CapitalUsageEntry:
    strategy_id: str
    governance_id: str
    allocated_capital: float
    deployed_capital: float
    realized_pnl: float
    timestamp: datetime


# ---------------------------------------------------------------------
# Deterministic Append-Only Ledger
# ---------------------------------------------------------------------


class CapitalUsageLedger:
    """
    Phase C5 — Capital Usage Ledger

    Guarantees:
    - Append-only
    - Immutable entries
    - Deterministic replay
    - No side effects
    """

    def __init__(self) -> None:
        self._entries: list[CapitalUsageEntry] = []

    def append(self, entry: CapitalUsageEntry) -> None:
        self._entries.append(entry)

    def entries(self) -> Tuple[CapitalUsageEntry, ...]:
        return tuple(self._entries)