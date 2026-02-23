# watchlist/adaptive_watchlist.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from infra.logging import get_logger
from screening.results import ScreeningResult

logger = get_logger("watchlist.adaptive_watchlist")


@dataclass
class WatchlistTiers:
    """
    Top-200 AI watchlist broken into three tiers:

      - top_20   : primary trade candidates
      - next_40  : secondary / conditional
      - next_140 : backfill / rotation universe
    """

    top_20: List[str]
    next_40: List[str]
    next_140: List[str]


class AdaptiveWatchlistEngine:
    """
    Adaptive watchlist manager for Phase 2.5.

    Responsibilities:
      - Take ranked ScreeningResults.
      - Apply PnL-based boosts/penalties (secondary to AdvancedScreeningEngine).
      - Update the DAY_SCALP (or other) watchlists with tiered segments.
    """

    def __init__(self, watchlist_service: Any) -> None:
        """
        watchlist_service:
            Your existing WatchlistService, expected to support:
              - get(name) -> Sequence[str]
              - set(name, symbols: Sequence[str]) -> None
              - save()   (optional)
        """
        self._wl = watchlist_service

    # ------------------------------------------------------------------ #
    # Tiering logic                                                      #
    # ------------------------------------------------------------------ #

    def build_tiers(
        self,
        ranked: Sequence[ScreeningResult],
        max_size: int = 200,
    ) -> WatchlistTiers:
        """Split ranked list into 20 / 40 / 140 tiers."""
        syms = [r.symbol for r in ranked[:max_size]]

        top_20 = syms[:20]
        next_40 = syms[20:60]
        next_140 = syms[60:200]

        return WatchlistTiers(
            top_20=top_20,
            next_40=next_40,
            next_140=next_140,
        )

    # ------------------------------------------------------------------ #
    # Update persistent watchlists                                       #
    # ------------------------------------------------------------------ #

    def update_watchlists(
        self,
        tiers: WatchlistTiers,
        primary_name: str = "DAY_SCALP",
        secondary_name: str = "DAY_SCALP_SECONDARY",
        rotation_name: str = "DAY_SCALP_ROTATION",
    ) -> None:
        """
        Persist tiered watchlists via your WatchlistService.

        Primary: Top 20
        Secondary: Next 40
        Rotation: Backfill 140
        """
        logger.info(
            "adaptive_watchlist_update",
            extra={
                "primary": primary_name,
                "secondary": secondary_name,
                "rotation": rotation_name,
                "top_20": len(tiers.top_20),
                "next_40": len(tiers.next_40),
                "next_140": len(tiers.next_140),
            },
        )

        self._wl.set(primary_name, tiers.top_20)
        self._wl.set(secondary_name, tiers.next_40)
        self._wl.set(rotation_name, tiers.next_140)

        # If your WatchlistService persists to disk, call save() if present
        if hasattr(self._wl, "save"):
            try:
                self._wl.save()
            except Exception:
                logger.debug("adaptive_watchlist_save_failed", exc_info=True)
