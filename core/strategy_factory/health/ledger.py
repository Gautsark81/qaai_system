from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List

from core.strategy_factory.health.report import StrategyHealthReport


# ------------------------------------------------------------------
# Internal append-only list (WRITE-GUARDED)
# ------------------------------------------------------------------

class _AppendOnlyList(List):
    def _blocked(self, *args, **kwargs):
        raise RuntimeError("StrategyHealthLedger is append-only")

    # Block all mutators
    clear = _blocked
    pop = _blocked
    remove = _blocked
    reverse = _blocked
    sort = _blocked
    __setitem__ = _blocked
    __delitem__ = _blocked


# ------------------------------------------------------------------
# Immutable Ledger Entry
# ------------------------------------------------------------------

@dataclass(frozen=True)
class StrategyHealthLedgerEntry:
    sequence: int
    strategy_dna: str
    report: StrategyHealthReport
    timestamp: datetime


# ------------------------------------------------------------------
# Strategy Health Ledger (APPEND-ONLY)
# ------------------------------------------------------------------

class StrategyHealthLedger:
    """
    Phase 15.2 — Strategy Health Evidence Ledger

    Properties:
    - append-only
    - immutable entries
    - deterministic ordering
    - audit-grade
    """

    def __init__(self):
        self._entries: _AppendOnlyList = _AppendOnlyList()
        self._sequence: int = 0

    # --------------------------------------------------------------
    # Append (ONLY mutation allowed)
    # --------------------------------------------------------------

    def append(self, report: StrategyHealthReport) -> StrategyHealthLedgerEntry:
        self._sequence += 1

        entry = StrategyHealthLedgerEntry(
            sequence=self._sequence,
            strategy_dna=report.strategy_dna,
            report=report,
            timestamp=datetime.utcnow(),
        )

        # INTERNAL append is allowed
        list.append(self._entries, entry)
        return entry

    # --------------------------------------------------------------
    # Read-only accessors
    # --------------------------------------------------------------

    def history(self, strategy_dna: str) -> List[StrategyHealthLedgerEntry]:
        return [e for e in self._entries if e.strategy_dna == strategy_dna]

    def latest(self, strategy_dna: str) -> StrategyHealthLedgerEntry | None:
        entries = self.history(strategy_dna)
        return entries[-1] if entries else None
