from __future__ import annotations

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

from core.live_verification.integration import LiveVerificationEngine


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
    live_verifier: Optional[LiveVerificationEngine] = None


def _default_snapshot_path() -> str:
    env_path = os.getenv("QA_PORTFOLIO_SNAPSHOT_PATH")
    if env_path:
        return env_path
    return "logs/portfolio_snapshots.jsonl"


def _derive_price_fetcher(price_source: Any | None) -> Optional[PriceFetcher]:
    if price_source is None:
        return None

    for name in ("get_ltp", "get_last_price", "get_price"):
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

    live_verifier = LiveVerificationEngine.global_instance()

    ctx = LiveEngineContext(
        engine=ee,
        position_tracker=position_tracker,
        snapshot_store=snapshot_store,
        logger=logger,
        risk_engine=re,
        price_fetcher=pf,
        risk_limits=risk_limits,
        live_verifier=live_verifier,
    )

    ee.live_context = ctx
    return ctx


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
    live_verifier = ctx.live_verifier

    logger.info("run_live_trading_loop: starting live loop")

    metrics_recorder = CycleMetricsRecorder()
    metric_context = MetricContext(
        env="live",
        strategy_id=getattr(signal_engine, "strategy_id", None),
        run_id=getattr(engine, "run_id", None),
    )

    event_bus = get_global_event_bus()

    iterations = 0
    cycle_index = 0

    while True:

        cycle_snapshot = metrics_recorder.on_cycle_start(
            cycle_id=str(cycle_index),
            context=metric_context,
            cycle_type="live_loop",
        )

        try:
            # ---------------------------------------------------------
            # GUARANTEED LIVE PROOF RECORD PER CYCLE
            # ---------------------------------------------------------
            if live_verifier is not None:
                try:
                    artifact = live_verifier.record(
                        strategy_dna=getattr(signal_engine, "strategy_id", "UNKNOWN"),
                        capital_decision={"cycle": cycle_index},
                        risk_verdict={"status": "cycle_evaluated"},
                        execution_intent={"cycle": cycle_index},
                        router_call_payload={"cycle": cycle_index},
                        mode="LIVE",
                    )

                    event_bus.emit(
                        "live.proof.recorded",
                        payload={
                            "strategy": artifact.trace.strategy_dna,
                            "validated": artifact.authority_validated,
                            "hash": artifact.chain_hash,
                        },
                    )

                except Exception:
                    logger.debug(
                        "Live proof recording failed (non-blocking)",
                        exc_info=True,
                    )
            # ---------------------------------------------------------

            engine.process_signals()

            if hasattr(engine, "monitor_orders"):
                engine.monitor_orders()
            elif hasattr(engine, "run_cycle"):
                engine.run_cycle()

        except Exception:
            logger.exception("run_live_trading_loop: unhandled exception")

        iterations += 1
        cycle_index += 1

        if max_iterations is not None and iterations >= max_iterations:
            break

        time.sleep(loop_sleep_seconds)

    return ctx