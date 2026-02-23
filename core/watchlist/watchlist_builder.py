from datetime import datetime, timezone
from typing import List, Optional

from core.contracts.screening import ScreeningResult
from core.live_ops.watchlist import WatchlistEntry, WatchlistManifest


class WatchlistBuilder:
    """
    Deterministic, institutional-grade watchlist builder.

    Input  : List[ScreeningResult]
    Output : WatchlistManifest

    Governance rules:
    - Deterministic by default
    - No implicit time dependence
    - Runtime timestamps must be explicitly injected
    """

    def __init__(self, max_symbols: int = 10, min_score: float = 0.5):
        self.max_symbols = max_symbols
        self.min_score = min_score

    def build(
        self,
        results: List[ScreeningResult],
        *,
        generated_at: Optional[datetime] = None,
    ) -> WatchlistManifest:
        """
        Build watchlist manifest.

        generated_at:
        - None  → deterministic epoch timestamp (test / replay safe)
        - datetime → explicit runtime timestamp (UI / live ops)
        """

        # ----------------------------
        # Deterministic timestamp
        # ----------------------------
        if generated_at is None:
            generated_at = datetime(1970, 1, 1, tzinfo=timezone.utc)

        # ----------------------------
        # 1. Filter passed results
        # ----------------------------
        passed = [r for r in results if r.passed]

        # ----------------------------
        # 2. Score threshold
        # ----------------------------
        qualified = [r for r in passed if r.score >= self.min_score]

        # ----------------------------
        # 3. Deterministic ranking
        #    (score desc, symbol asc)
        # ----------------------------
        ranked = sorted(
            qualified,
            key=lambda r: (-r.score, r.symbol),
        )[: self.max_symbols]

        entries: List[WatchlistEntry] = []

        for rank, r in enumerate(ranked, start=1):
            entries.append(
                WatchlistEntry(
                    symbol=r.symbol,
                    rank=rank,
                    confidence=round(float(r.score), 3),
                    source="screening",
                    reasons=list(r.reasons),
                )
            )

        return WatchlistManifest(
            generated_at=generated_at,
            entries=entries,
            constraints={
                "max_symbols": self.max_symbols,
                "min_score": self.min_score,
            },
        )
