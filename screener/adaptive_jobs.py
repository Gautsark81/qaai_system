# screener/adaptive_jobs.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from infra.logging import get_logger
from infra.time_utils import now_ist
from screening.advanced_engine import (
    AdvancedScreeningEngine,
    AdvancedScreenConfig,
    MarketRegime,
)
from watchlist.adaptive_watchlist import AdaptiveWatchlistEngine, WatchlistTiers

logger = get_logger("screener.adaptive_jobs")


@dataclass
class MarketState:
    """
    Minimal snapshot of market-wide state, used for:
      - regime detection
      - dynamic refresh decisions
    """

    nifty_return_5m: float = 0.0
    vix_change: float = 0.0
    realized_vol_regime: MarketRegime = MarketRegime.UNKNOWN
    l2_breadth_flip_count: int = 0  # count of symbols where L2 imbalance flipped


class AdaptiveScreenerJob:
    """
    Orchestrates Phase 2.5:

      universe -> AdvancedScreeningEngine -> AdaptiveWatchlistEngine

    This job is intended to be called from your root scheduler with a
    dynamic cadence (3m / 10m / 20-30m) based on MarketState.
    """

    def __init__(
        self,
        screening_ctx: Any,
        watchlist_service: Any,
        engine: Optional[AdvancedScreeningEngine] = None,
        config: Optional[AdvancedScreenConfig] = None,
    ) -> None:
        self._ctx = screening_ctx
        self._aw = AdaptiveWatchlistEngine(watchlist_service)
        self._engine = engine or AdvancedScreeningEngine(config=config)
        self._config = config or self._engine._config

    # ------------------------------------------------------------------ #
    # Dynamic refresh logic                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def compute_refresh_interval_seconds(state: MarketState) -> int:
        """
        Dynamic refresh as per your spec:

          - High vol  -> ~3 minutes
          - Normal    -> ~10 minutes
          - Low vol   -> ~20-30 minutes
          - Immediate trigger when:
              * NIFTY ±0.5% in 5m
              * VIX > +2%
              * L2 imbalance flips in >15 stocks
        """
        # Immediate trigger consideration is responsibility of caller:
        # if any trigger fires, schedule this job "now".

        regime = state.realized_vol_regime

        if regime == MarketRegime.HIGH_VOL:
            return 3 * 60
        if regime == MarketRegime.LOW_VOL:
            return 25 * 60  # midpoint of 20–30m
        return 10 * 60  # NORMAL / UNKNOWN

    # ------------------------------------------------------------------ #
    # Job execution                                                      #
    # ------------------------------------------------------------------ #

    def run_once(self, state: Optional[MarketState] = None) -> WatchlistTiers:
        """
        Execute one full cycle:

          1) Rank universe using AdvancedScreeningEngine.
          2) Build Top-200 tiers (20/40/140).
          3) Persist to watchlists.

        Returns the tiers for introspection or logging.
        """
        state = state or MarketState()
        as_of = now_ist()

        logger.info(
            "adaptive_screener_job_start",
            extra={
                "ts": as_of.isoformat(),
                "regime": state.realized_vol_regime.value,
                "nifty_return_5m": state.nifty_return_5m,
                "vix_change": state.vix_change,
                "l2_breadth_flips": state.l2_breadth_flip_count,
            },
        )

        ranked = self._engine.rank_universe(
            self._ctx,
            regime=state.realized_vol_regime,
        )

        tiers = self._aw.build_tiers(ranked, max_size=self._config.force_top_n)
        self._aw.update_watchlists(tiers)

        logger.info(
            "adaptive_screener_job_done",
            extra={
                "ts": as_of.isoformat(),
                "top_20": len(tiers.top_20),
                "next_40": len(tiers.next_40),
                "next_140": len(tiers.next_140),
            },
        )

        return tiers
