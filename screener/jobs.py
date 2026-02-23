from __future__ import annotations

from typing import List

from infra.time_utils import now_ist
from infra.logging import get_logger

from data.tick_store import TickStore
from data.ohlcv_store import OHLCVStore
from data.feature_store import FeatureStore

from screening.context import ScreeningContext
from core.screening.engine import ScreeningEngine, ScreenConfig
from watchlist.service import WatchlistService

logger = get_logger(__name__)


class ScreenerJobs:
    """
    Scheduler-facing orchestration wrapper.

    Responsibilities:
    - Build ScreeningContext
    - Invoke ScreeningEngine
    - Populate Watchlists

    Deterministic. Test-aligned. Bootstrap-safe.
    """

    def __init__(
        self,
        tick_store: TickStore,
        ohlcv_store: OHLCVStore,
        feature_store: FeatureStore,
        watchlist: WatchlistService,
        universe: List[str],
    ) -> None:
        self._tick_store = tick_store
        self._ohlcv_store = ohlcv_store
        self._feature_store = feature_store
        self._watchlist = watchlist
        self._universe = universe

        self._engine = ScreeningEngine()

    def _ensure_non_empty(self, symbols: List[str]) -> List[str]:
        """
        Safety fallback:
        If screening yields nothing (common in cold-start),
        populate from universe deterministically.
        """
        if symbols:
            return symbols

        logger.warning(
            "screening_empty_fallback",
            extra={"fallback_size": len(self._universe)},
        )
        return sorted(self._universe)

    def run_pre_market_screen(self) -> None:
        as_of = now_ist()

        ctx = ScreeningContext.from_universe(
            tick_store=self._tick_store,
            ohlcv_store=self._ohlcv_store,
            feature_store=self._feature_store,
            universe=self._universe,
            timeframe="5m",
            as_of=as_of,
        )

        cfg = ScreenConfig(
            name="PRE_MARKET_5M",
            timeframe="5m",
            top_n=50,
            min_liquidity=0.0,
        )

        decisions = self._engine.run_screen(ctx, cfg)
        symbols = [d.symbol for d in decisions if d.passed]

        symbols = self._ensure_non_empty(symbols)

        self._watchlist.set("DAY_SCALP", symbols)

        logger.info(
            "pre_market_screen_complete",
            extra={
                "as_of": as_of.isoformat(),
                "symbols": len(symbols),
            },
        )

    def run_intraday_refresh(self) -> None:
        as_of = now_ist()

        ctx = ScreeningContext.from_universe(
            tick_store=self._tick_store,
            ohlcv_store=self._ohlcv_store,
            feature_store=self._feature_store,
            universe=self._universe,
            timeframe="1m",
            as_of=as_of,
        )

        cfg = ScreenConfig(
            name="INTRADAY_1M",
            timeframe="1m",
            top_n=50,
            min_liquidity=0.0,
            watchlist_name="DAY_SCALP",
        )

        decisions = self._engine.run_screen(ctx, cfg)
        symbols = [d.symbol for d in decisions if d.passed]

        symbols = self._ensure_non_empty(symbols)

        self._watchlist.set("INTRADAY_CORE", symbols)

        logger.info(
            "intraday_screen_complete",
            extra={
                "as_of": as_of.isoformat(),
                "symbols": len(symbols),
            },
        )
