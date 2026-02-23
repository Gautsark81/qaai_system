from __future__ import annotations

from typing import Dict

from core.watchlist.errors import WatchlistViolation
from core.watchlist.manager import WatchlistManager


class LiveBrokerStub:
    """
    Stub for live broker.

    This is the FINAL symbol-aware execution gate for LIVE trading.
    All hard invariants that must never be violated in real markets
    are enforced here.

    Replaced later with a real broker adapter (Dhan, Zerodha, etc.),
    but the invariants in this layer must remain identical.
    """

    def place_order(
        self,
        *,
        symbol: str,
        qty: int,
        side: str,
        price: float,
    ) -> Dict:
        # ======================================================
        # MUST-FIX #1 — HARD WATCHLIST INVARIANT (LIVE ONLY)
        # ======================================================
        watchlist = WatchlistManager.get_active_snapshot()

        if watchlist is None:
            raise RuntimeError(
                "Live trading attempted without an active WatchlistSnapshot"
            )

        if symbol not in watchlist.entries:
            raise WatchlistViolation(
                f"Live trade blocked: symbol '{symbol}' "
                f"is not in the active watchlist"
            )

        # ======================================================
        # EXECUTION (STUB)
        # ======================================================
        # No real API calls yet — deterministic stub only.
        # All execution engines and live adapters must respect
        # the same invariants enforced here.
        return {
            "status": "ACCEPTED",
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "price": price,
        }
