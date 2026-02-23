(venv) PS C:\Users\topta\OneDrive\Documents\qaai_system> type apps/run_live_engine.py
from __future__ import annotations

"""
Helpers to build a live ExecutionEngine + PositionTracker bundle and
log/persist portfolio snapshots.

This module is intentionally thin and orchestration-focused. It does NOT
own any strategy / signal / risk logic â€“ it just wires:

    SignalEngine
        -> ExecutionEngine
        -> PositionTracker
        -> PortfolioState
        -> SnapshotStore (JSONL history)
        -> (optional) RiskEngine
"""

import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple

from qaai_system.execution.execution_engine import ExecutionEngine
from portfolio.position_tracker import PositionTracker
from portfolio.portfolio_state import PortfolioState
from portfolio.snapshot_store import SnapshotStore
from risk.risk_engine import RiskEngine
from risk.risk_limits import RiskLimits

from analytics.metrics import (
    CycleMetricsRecorder,
    MetricContext,
)
from infra.event_bus import get_global_event_bus

# ---------------------------------------------------------------------------
# ðŸ” ADDITION 1: Live Verification Import (NON-INTRUSIVE)
# ---------------------------------------------------------------------------
from core.live_verification.integration import LiveVerificationEngine
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

PriceFetcher = Callable[[str], float]


@dataclass
class LiveEngineContext:
    engine: ExecutionEngine
    position_tracker: PositionTracker
    snapshot_store: SnapshotStore
    logger: Any
    risk_engine: Optional[RiskEngine] = None
    price_fetcher: Optional[PriceFetcher] = None
    risk_limits: Optional[RiskLimits] = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _default_snapshot_path() -> str:
    env_path = os.getenv("QA_PORTFOLIO_SNAPSHOT_PATH")
    if env_path:
        return env_path
    return "logs/portfolio_snapshots.jsonl"


def _derive_price_fetcher(price_source: Any | None) -> Optional[PriceFetcher]:
    if price_source is None:
        return None

    candidates = ("get_ltp", "get_last_price", "get_price")
    for name in candidates:
        if hasattr(price_source, name):
            method = getattr(price_source, name)

            def fetch(symbol: str, _m=method) -> float:
                return float(_m(symbol))

            return fetch

    return None


def _build_risk_engine_if_needed(
    risk_engine: Optional[RiskEngine],
    risk_limits: Optional[RiskLimits],
    logger: Any,
) -> Optional[RiskEngine]:

    if risk_engine is not None:
        return risk_engine

    if risk_limits is not None:
        return RiskEngine(limits=risk_limits, logger=logger)

    return None


# ---------------------------------------------------------------------------
# Public API â€“ builders
# ---------------------------------------------------------------------------


def build_live_engine(
    signal_engine: Any,
    order_manager: Any,
    safe_broker: Any,
    logger: Any,
    *,
    price_fetcher: Optional[PriceFetcher] = None,
    snapshot_path: Optional[str] = None,
    risk_engine: Optional[RiskEngine] = None,
    risk_limits: Optional[RiskLimits] = None,
) -> Tuple[ExecutionEngine, PositionTracker]:

    pf = price_fetcher or _derive_price_fetcher(safe_broker)
    path = snapshot_path or _default_snapshot_path()
    snapshot_store = SnapshotStore(path=path)
    position_tracker = PositionTracker(price_fetcher=pf, logger=logger)

    ee = ExecutionEngine(
        signal_engine=signal_engine,
        order_manager=order_manager,
        broker_adapter=safe_broker,
        config={"exec_mode": "live"},
    )

    ee.position_tracker = position_tracker

    re = _build_risk_engine_if_needed(risk_engine, risk_limits, logger)
    if re is not None:
        ee.risk_engine = re

    ee.live_context = LiveEngineContext(
        engine=ee,
        position_tracker=position_tracker,
        snapshot_store=snapshot_store,
        logger=logger,
        risk_engine=re,
        price_fetcher=pf,
        risk_limits=risk_limits,
    )

    return ee, position_tracker


def build_live_context(
    signal_engine: Any,
    order_manager: Any,
    safe_broker: Any,
    logger: Any,
    *,
    price_fetcher: Optional[PriceFetcher] = None,
    snapshot_path: Optional[str] = None,
    risk_engine: Optional[RiskEngine] = None,
    risk_limits: Optional[RiskLimits] = None,
) -> LiveEngineContext:

    pf = price_fetcher or _derive_price_fetcher(safe_broker)
    path = snapshot_path or _default_snapshot_path()
    snapshot_store = SnapshotStore(path=path)
    position_tracker = PositionTracker(price_fetcher=pf, logger=logger)

    ee = ExecutionEngine(
        signal_engine=signal_engine,
        order_manager=order_manager,
        broker_adapter=safe_broker,
        config={"exec_mode": "live"},
    )

    ee.position_tracker = position_tracker

    re = _build_risk_engine_if_needed(risk_engine, risk_limits, logger)
    if re is not None:
        ee.risk_engine = re

    ctx = LiveEngineContext(
        engine=ee,
        position_tracker=position_tracker,
        snapshot_store=snapshot_store,
        logger=logger,
        risk_engine=re,
        price_fetcher=pf,
        risk_limits=risk_limits,
    )

    ee.live_context = ctx
    return ctx


# ---------------------------------------------------------------------------
# Public API â€“ snapshot logging
# ---------------------------------------------------------------------------


def log_and_persist_portfolio(
    position_tracker: PositionTracker,
    logger: Any,
    *,
    equity: Optional[float] = None,
    cash: Optional[float] = None,
    snapshot_path: Optional[str] = None,
) -> None:

    position_tracker.log_snapshot(equity=equity, cash=cash)

    try:
        state = PortfolioState.from_tracker(
            position_tracker,
            equity=equity,
            cash=cash,
        )
        path = snapshot_path or _default_snapshot_path()
        store = SnapshotStore(path=path)
        store.append_snapshot(state.snapshot)

        try:
            bus = get_global_event_bus()
            bus.emit(
                "portfolio.snapshot",
                payload={"snapshot": state.snapshot},
                metadata={"equity": equity, "cash": cash},
            )
        except Exception:
            if logger:
                logger.debug("event_bus emit failed", exc_info=True)

    except Exception:
        if logger:
            logger.debug("snapshot persistence failed", exc_info=True)


# ---------------------------------------------------------------------------
# Public API â€“ opinionated live loop helper
# ---------------------------------------------------------------------------


def run_live_trading_loop(
    signal_engine: Any,
    order_manager: Any,
    safe_broker: Any,
    logger: Any,
    *,
    loop_sleep_seconds: float = 1.0,
    max_iterations: Optional[int] = None,
    price_fetcher: Optional[PriceFetcher] = None,
    snapshot_path: Optional[str] = None,
    risk_engine: Optional[RiskEngine] = None,
    risk_limits: Optional[RiskLimits] = None,
) -> LiveEngineContext:

    ctx = build_live_context(
        signal_engine=signal_engine,
        order_manager=order_manager,
        safe_broker=safe_broker,
        logger=logger,
        price_fetcher=price_fetcher,
        snapshot_path=snapshot_path,
        risk_engine=risk_engine,
        risk_limits=risk_limits,
    )

    engine = ctx.engine
    tracker = ctx.position_tracker

    logger.info("run_live_trading_loop: starting live loop")

    metrics_recorder = CycleMetricsRecorder()
    metric_context = MetricContext(
        env="live",
        strategy_id=getattr(signal_engine, "strategy_id", None),
        run_id=getattr(engine, "run_id", None),
    )

    event_bus = get_global_event_bus()

    # -----------------------------------------------------------------------
    # ðŸ” ADDITION 2: Shared Live Verifier (outside loop)
    # -----------------------------------------------------------------------
    live_verifier = LiveVerificationEngine.global_instance()
    # -----------------------------------------------------------------------

    iterations = 0
    cycle_index = 0

    while True:

        cycle_snapshot = metrics_recorder.on_cycle_start(
            cycle_id=str(cycle_index),
            context=metric_context,
            cycle_type="live_loop",
            extra={"loop_sleep_seconds": loop_sleep_seconds},
        )

        event_bus.emit(
            "live.cycle.start",
            payload={"cycle_index": cycle_index},
            metadata={
                "strategy_id": metric_context.strategy_id,
                "run_id": metric_context.run_id,
                "loop_sleep_seconds": loop_sleep_seconds,
            },
        )

        num_orders = 0
        num_active_orders = 0
        num_fills = 0
        num_errors = 0

        try:
            engine.process_signals()

            if hasattr(engine, "monitor_orders"):
                engine.monitor_orders()
            elif hasattr(engine, "run_cycle"):
                engine.run_cycle()

            # -----------------------------------------------------------------
            # ðŸ” ADDITION 3: Record Live Proof (SAFE + NON-INTRUSIVE)
            # -----------------------------------------------------------------
            try:
                live_verifier.record(
                    strategy_dna=str(getattr(signal_engine, "strategy_id", "unknown")),
                    capital_decision={"source": "live_loop"},
                    risk_verdict={"status": "unknown"},
                    execution_intent={"source": "live_loop"},
                    router_call_payload={"mode": "live"},
                    mode="live",
                )
            except Exception:
                logger.debug("live verification failed", exc_info=True)
            # -----------------------------------------------------------------

            log_and_persist_portfolio(tracker, logger, snapshot_path=snapshot_path)

            metrics_recorder.on_cycle_success(
                cycle=cycle_snapshot,
                context=metric_context,
                num_orders=num_orders,
                num_active_orders=num_active_orders,
                num_fills=num_fills,
                num_errors=num_errors,
            )

            event_bus.emit(
                "live.cycle.success",
                payload={
                    "cycle_index": cycle_index,
                    "num_orders": num_orders,
                    "num_active_orders": num_active_orders,
                    "num_fills": num_fills,
                    "num_errors": num_errors,
                },
                metadata={
                    "strategy_id": metric_context.strategy_id,
                    "run_id": metric_context.run_id,
                },
            )

        except Exception as exc:
            num_errors += 1

            metrics_recorder.on_cycle_failure(
                cycle=cycle_snapshot,
                context=metric_context,
                exc=exc,
                extra={"cycle_index": cycle_index},
            )

            event_bus.emit(
                "live.cycle.failure",
                payload={
                    "cycle_index": cycle_index,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                },
                metadata={
                    "strategy_id": metric_context.strategy_id,
                    "run_id": metric_context.run_id,
                },
            )

            logger.exception("run_live_trading_loop: unhandled exception")

        iterations += 1
        cycle_index += 1

        if max_iterations is not None and iterations >= max_iterations:
            logger.info(
                "run_live_trading_loop: reached max_iterations=%s, exiting",
                max_iterations,
            )
            break

        time.sleep(loop_sleep_seconds)

    return ctx
(venv) PS C:\Users\topta\OneDrive\Documents\qaai_system>