# orchestration/screener_orchestrator.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional

from infra.logging import get_logger

from context.live_context import LiveContext  # or ScreeningContext in offline runs
from watchlist.service import WatchlistService

from screening.advanced_engine import (
    AdvancedScreeningEngine,
    AdvancedScreenConfig,
    MarketRegime,
)
from screener.adaptive_jobs import AdaptiveScreenerJob, MarketState
from analytics.pnl_feedback import PnLFeedbackSource, TradeRecord
from ml.ise_ml_brain import ISEMLBrainStub

logger = get_logger("orchestration.screener_orchestrator")


# Optional: small protocol to decouple from your exact OrderManager API
class OrderManagerLike:
    """
    Minimal interface this orchestrator expects from OrderManager.

    If your real OrderManager has a different API, you can:
      - implement an adapter that conforms to this
      - or tweak the ingestion code below.
    """

    def get_recent_fills(self) -> Iterable[dict]:
        """
        Should return a sequence of dicts with at least:
          - 'symbol'
          - 'pnl'       (realized PnL for that fill or aggregate)
          - 'ts_ns'     (timestamp in ns / ms / s – consistent per system)
        """
        ...


@dataclass
class ScreenerOrchestratorConfig:
    """
    Configuration for the Phase 2.5 Screener Orchestrator.
    """

    screen_config: AdvancedScreenConfig = AdvancedScreenConfig()
    # How many recent trades to consider in PnL feedback
    pnl_lookback_trades: int = 200


class ScreenerOrchestrator:
    """
    High-level orchestrator for Phase 2.5 Screening + Adaptive Watchlists.

    Responsibilities:
      - Instantiate AdvancedScreeningEngine with ML Brain + PnL feedback.
      - Maintain PnL feedback by ingesting trades from OrderManager.
      - Run AdaptiveScreenerJob to:
          * rank universe
          * build tiered watchlists (20/40/140)
          * persist via WatchlistService
      - Provide a single entrypoint that your root orchestrator/scheduler
        can call at dynamic intervals.
    """

    def __init__(
        self,
        ctx: LiveContext,
        watchlist_service: WatchlistService,
        order_manager: Optional[OrderManagerLike] = None,
        ml_brain: Optional[Any] = None,
        config: Optional[ScreenerOrchestratorConfig] = None,
    ) -> None:
        self._ctx = ctx
        self._watchlists = watchlist_service
        self._order_mgr = order_manager

        self._cfg = config or ScreenerOrchestratorConfig()

        # PnL feedback source plugged into AdvancedScreeningEngine
        self._pnl_feedback = PnLFeedbackSource(
            lookback_trades=self._cfg.pnl_lookback_trades
        )

        # If no ML brain supplied, use the stub (safe default)
        self._ml_brain = ml_brain or ISEMLBrainStub()

        # Advanced screening engine + job
        self._engine = AdvancedScreeningEngine(
            ml_brain=self._ml_brain,
            pnl_feedback=self._pnl_feedback,
            config=self._cfg.screen_config,
        )
        self._job = AdaptiveScreenerJob(
            screening_ctx=self._ctx,
            watchlist_service=self._watchlists,
            engine=self._engine,
            config=self._cfg.screen_config,
        )

    # ------------------------------------------------------------------ #
    # PnL feedback wiring                                                #
    # ------------------------------------------------------------------ #

    def _ingest_recent_trades_from_order_manager(self) -> None:
        """
        Pull recent fills/trades from OrderManager and update PnL feedback.

        This should be called each time before we run the screener, so
        that ranking incorporates the latest trade performance.
        """
        if self._order_mgr is None:
            return

        try:
            raw_fills = list(self._order_mgr.get_recent_fills())
        except Exception:
            logger.debug("screener_orch_get_recent_fills_failed", exc_info=True)
            return

        records: list[TradeRecord] = []
        for f in raw_fills:
            sym = f.get("symbol")
            pnl = f.get("pnl")
            ts_ns = f.get("ts_ns")
            if sym is None or pnl is None or ts_ns is None:
                continue
            try:
                records.append(
                    TradeRecord(
                        symbol=str(sym),
                        pnl=float(pnl),
                        ts_ns=int(ts_ns),
                    )
                )
            except Exception:
                # ignore badly formatted rows
                continue

        if not records:
            return

        self._pnl_feedback.ingest_trades(records)

    # ------------------------------------------------------------------ #
    # Public entrypoint for root orchestrator                            #
    # ------------------------------------------------------------------ #

    def run_adaptive_screen_once(
        self,
        regime: MarketRegime = MarketRegime.UNKNOWN,
        nifty_return_5m: float = 0.0,
        vix_change: float = 0.0,
        l2_breadth_flips: int = 0,
    ):
        """
        Main method your root orchestrator should call.

        Example usage in your orchestrator.py:

            self._screener_orch.run_adaptive_screen_once(
                regime=current_regime,
                nifty_return_5m=metrics.nifty_return_5m,
                vix_change=metrics.vix_change,
                l2_breadth_flips=l2_metrics.breadth_flips,
            )

        This will:
          - ingest latest trades → PnL feedback
          - execute AdvancedScreeningEngine → ranked universe
          - build Top-200 tiers (20/40/140)
          - persist to DAY_SCALP / DAY_SCALP_SECONDARY / DAY_SCALP_ROTATION
        """
        # 1) Update PnL feedback from latest trades
        self._ingest_recent_trades_from_order_manager()

        # 2) Construct MarketState
        state = MarketState(
            nifty_return_5m=float(nifty_return_5m),
            vix_change=float(vix_change),
            realized_vol_regime=regime,
            l2_breadth_flip_count=int(l2_breadth_flips),
        )

        # 3) Delegate to AdaptiveScreenerJob
        tiers = self._job.run_once(state)

        # You can add custom logging/metrics here if desired
        logger.info(
            "screener_orch_run_complete",
            extra={
                "regime": regime.value,
                "top_20": len(tiers.top_20),
                "next_40": len(tiers.next_40),
                "next_140": len(tiers.next_140),
            },
        )

        return tiers
