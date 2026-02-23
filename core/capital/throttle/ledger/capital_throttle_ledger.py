from typing import Tuple

from .capital_throttle_ledger_entry import CapitalThrottleLedgerEntry


class CapitalThrottleLedger:
    """
    Append-only, deterministic ledger for capital throttle events.
    """

    def __init__(self):
        self._entries: list[CapitalThrottleLedgerEntry] = []

    def append(self, entry: CapitalThrottleLedgerEntry) -> None:
        self._entries.append(entry)

    @property
    def entries(self) -> Tuple[CapitalThrottleLedgerEntry, ...]:
        return tuple(self._entries)
