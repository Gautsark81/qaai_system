from typing import Tuple

from core.capital.ledger.capital_scaling_ledger_entry import (
    CapitalScalingLedgerEntry,
)


class CapitalScalingLedger:
    """
    Append-only ledger for capital scaling events.
    Phase 12.2 — contract-complete, logic-minimal.
    """

    def __init__(self):
        self._entries: Tuple[CapitalScalingLedgerEntry, ...] = ()

    @property
    def entries(self) -> Tuple[CapitalScalingLedgerEntry, ...]:
        return self._entries

    def append(self, entry: CapitalScalingLedgerEntry) -> None:
        """
        Append a new immutable ledger entry.
        """
        self._entries = (*self._entries, entry)
