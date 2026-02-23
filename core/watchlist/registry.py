# core/watchlist/registry.py

from typing import Dict, List

from .entry import WatchlistEntry


class WatchlistRegistry:
    def __init__(self) -> None:
        # symbol -> WatchlistEntry
        self._entries: Dict[str, WatchlistEntry] = {}

    # --- Core API ---

    def add(self, symbol: str, composite_verdict) -> WatchlistEntry:
        """
        Add a symbol to the watchlist if (and only if) composite screening passed.
        Idempotent for ACTIVE/SUSPENDED entries.
        RETIRED entries are terminal and cannot be re-added.
        """
        if not getattr(composite_verdict, "passed", False):
            raise ValueError("Composite screening failed; cannot add to watchlist")

        if symbol in self._entries:
            entry = self._entries[symbol]
            if entry.status == "RETIRED":
                raise ValueError("Symbol is retired and cannot be re-added")
            # Idempotent: return existing entry
            return entry

        entry = WatchlistEntry(
            symbol=symbol,
            screening_passed=True,
            status="ACTIVE",
            suspension_reason=None,
        )
        self._entries[symbol] = entry
        return entry

    def suspend(self, symbol: str, reason: str) -> None:
        """
        Suspend an ACTIVE entry with an explicit reason.
        """
        entry = self._require(symbol)

        if entry.status == "RETIRED":
            raise ValueError("Cannot suspend a retired entry")

        self._entries[symbol] = WatchlistEntry(
            symbol=entry.symbol,
            screening_passed=entry.screening_passed,
            status="SUSPENDED",
            suspension_reason=reason,
        )

    def retire(self, symbol: str, reason: str) -> None:
        """
        Retire an entry permanently. This is terminal.
        """
        entry = self._require(symbol)

        self._entries[symbol] = WatchlistEntry(
            symbol=entry.symbol,
            screening_passed=entry.screening_passed,
            status="RETIRED",
            suspension_reason=reason,
        )

    def get(self, symbol: str) -> WatchlistEntry:
        """
        Retrieve a single watchlist entry.
        """
        return self._require(symbol)

    def list_entries(self) -> List[WatchlistEntry]:
        """
        Deterministic ordering by symbol.
        """
        return [self._entries[s] for s in sorted(self._entries.keys())]

    def size(self) -> int:
        """
        Number of entries in the watchlist.
        """
        return len(self._entries)

    # --- Internal helpers ---

    def _require(self, symbol: str) -> WatchlistEntry:
        if symbol not in self._entries:
            raise KeyError(f"Symbol not found in watchlist: {symbol}")
        return self._entries[symbol]
