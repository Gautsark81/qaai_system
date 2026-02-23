# core/strategy_factory/screening/watchlist_engine.py

from __future__ import annotations

from decimal import Decimal

from .screening_models import ScreeningResult
from .meta_alpha_models import MetaAlphaReport
from .watchlist_models import (
    WatchlistEntry,
    WatchlistReport,
)
from .watchlist_hash import compute_watchlist_hash


class IntelligentWatchlistConstructor:
    """
    C5.8 — Advisory Watchlist Intelligence

    HARD RULES:
    - Deterministic
    - Advisory only
    - No lifecycle mutation
    - No capital mutation
    - No promotion logic
    - No registry mutation
    """

    def build(
        self,
        *,
        screening_result: ScreeningResult,
        meta_alpha: MetaAlphaReport,
    ) -> WatchlistReport:

        scores = screening_result.scores

        if not scores:
            entries = ()
            return WatchlistReport(
                entries=entries,
                recommended_size=0,
                state_hash=compute_watchlist_hash(entries, 0),
            )

        # ---------------------------------------------------
        # 1️⃣ Base ranking (already deterministic)
        # ---------------------------------------------------
        entries = tuple(
            WatchlistEntry(
                strategy_dna=s.strategy_dna,
                rank=s.rank,
            )
            for s in scores
        )

        # ---------------------------------------------------
        # 2️⃣ Adaptive breadth from meta-alpha
        # ---------------------------------------------------
        breadth_signal = next(
            (
                s.value
                for s in meta_alpha.signals
                if s.signal_type == "ALPHA_BREADTH"
            ),
            Decimal(len(entries)),
        )

        # Cap recommended size by breadth
        recommended_size = min(
            len(entries),
            int(breadth_signal),
        )

        return WatchlistReport(
            entries=entries,
            recommended_size=recommended_size,
            state_hash=compute_watchlist_hash(
                entries,
                recommended_size,
            ),
        )