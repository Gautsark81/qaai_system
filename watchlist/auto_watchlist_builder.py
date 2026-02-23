from __future__ import annotations

from typing import Optional, List

from infra.logging import get_logger
from core.watchlist.builder import build_watchlist

logger = get_logger(__name__)

# ------------------------------------------------------------------
# Explicit symbols required for test patching
# ------------------------------------------------------------------

class DhanClient:
    """
    Placeholder client.
    Real implementation is injected or patched in tests.
    """

    def get_top_nse_stocks_by_volume(self, top_n: int) -> List[str]:
        raise NotImplementedError


class DBClient:
    """
    Placeholder DB client.
    Real implementation is injected or patched in tests.
    """

    def clear_watchlist(self) -> None:
        raise NotImplementedError

    def insert_watchlist(self, symbols: List[str]) -> None:
        raise NotImplementedError


# ------------------------------------------------------------------
# Auto Watchlist Builder
# ------------------------------------------------------------------

class AutoWatchlistBuilder:
    """
    Deterministic, test-safe auto watchlist updater.

    Responsibilities:
    - Fetch symbols from broker client
    - Clear existing watchlist state
    - Persist new watchlist via DB client
    - Optionally run pure build_watchlist logic
    - Never raise (scheduler-safe)
    """

    def __init__(
        self,
        dhan_client: Optional[DhanClient] = None,
        db_client: Optional[DBClient] = None,
        top_n: int = 50,
        **build_kwargs,
    ):
        self.dhan_client = dhan_client or DhanClient()
        self.db_client = db_client or DBClient()
        self.top_n = top_n
        self.build_kwargs = build_kwargs

    # --------------------------------------------------------------
    # Public API (tests expect this)
    # --------------------------------------------------------------

    def update_watchlist(self):
        """
        Legacy-compatible entrypoint.
        Must never raise.
        """
        try:
            return self.run()
        except Exception as e:
            logger.error(
                "auto_watchlist_update_failed",
                extra={"error": str(e)},
            )
            return None

    # --------------------------------------------------------------
    # Core logic
    # --------------------------------------------------------------

    def run(self):
        # 1. Fetch symbols (mocked in tests)
        symbols = self.dhan_client.get_top_nse_stocks_by_volume(self.top_n)

        # 2. Clear existing watchlist
        self.db_client.clear_watchlist()

        # 3. Persist new watchlist (TEST-REQUIRED)
        self.db_client.insert_watchlist(symbols)

        # 4. Optional: run pure builder logic (ranking, metadata, etc.)
        #    This must NOT handle persistence
        return build_watchlist(
            symbols=symbols,
            **self.build_kwargs,
        )
