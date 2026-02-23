from typing import Iterable, Optional

from core.watchlist.builder import WatchlistBuilder
from core.watchlist.snapshot import build_snapshot
from core.watchlist.models import WatchlistSnapshot


class WatchlistManager:
    """
    Canonical Watchlist Manager.

    Design:
    - Stateless
    - Deterministic
    - Explicit watchlist artifacts

    NOTE:
    - get_active_snapshot() exists ONLY as a test seam.
    - Production code MUST pass snapshots explicitly.
    """

    def __init__(
        self,
        max_symbols: Optional[int] = None,
        min_score: float = 0.0,
        source: str = "screening",
    ):
        self.builder = WatchlistBuilder(
            max_symbols=max_symbols,
            min_score=min_score,
            source=source,
        )

    # --------------------------------------------------
    # Build watchlist from screening output
    # --------------------------------------------------

    def build(self, screening_results: Iterable) -> WatchlistSnapshot:
        manifest = self.builder.build(screening_results)
        return build_snapshot(manifest.entries)

    # --------------------------------------------------
    # TEST SEAM ONLY (NO STATE)
    # --------------------------------------------------

    @classmethod
    def get_active_snapshot(cls) -> WatchlistSnapshot:
        """
        TEST SEAM ONLY.

        This method intentionally has no implementation.
        Tests may monkeypatch it to inject a snapshot.

        Production code must NEVER rely on this.
        """
        raise RuntimeError(
            "No active watchlist snapshot in production context"
        )
