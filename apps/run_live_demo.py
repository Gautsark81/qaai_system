from __future__ import annotations

"""
Supercharged live demo runner for qaai_system.

Shows:
- EventBus events
- DiagnosticsAgent logs
- Cycle metrics from run_live_trading_loop
- CLI + env-based configuration

Modes
-----
Currently supported:
- demo  : uses dummy SignalEngine / OrderManager / Broker (no real trading)

Env overrides
-------------
QA_LIVE_MAX_ITERS      -> default for --max-iters
QA_LIVE_LOOP_SLEEP     -> default for --sleep-seconds
QA_LIVE_LOG_LEVEL      -> default for --log-level
"""

import argparse
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from infra.diagnostics_agent import DiagnosticsAgent
from infra.logging import get_logger
from apps.run_live_engine import run_live_trading_loop


# ---------------------------------------------------------------------------
# Small env helpers
# ---------------------------------------------------------------------------


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_str(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value is not None else default


# ---------------------------------------------------------------------------
# Dummy components for demo mode
# ---------------------------------------------------------------------------


@dataclass
class DummySignalEngine:
    """
    Very small stub that pretends to produce some signals.

    In a real run you would inject your actual SignalEngine /
    strategy orchestrator here.
    """

    strategy_id: str = "demo_strategy"

    def generate_signals(self) -> List[Dict[str, Any]]:
        # In a real engine this would be complex; here we just return an empty list.
        return []


class DummyOrderManager:
    """
    Dummy order manager that satisfies the ExecutionEngine interface enough
    for demo purposes.
    """

    def place_orders(self, orders: List[Dict[str, Any]]) -> None:
        # No-op in demo mode
        return

    def poll_fills(self) -> List[Dict[str, Any]]:
        # No-op in demo mode
        return []


class DummyBroker:
    """
    Dummy broker adapter with minimal interface for demo runs.
    """

    def place_order(self, *args: Any, **kwargs: Any) -> None:
        # No-op in demo mode
        return

    def get_ltp(self, symbol: str) -> float:
        # Return a fake last-traded price for demo
        return 100.0


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Supercharged live demo runner for qaai_system",
    )

    parser.add_argument(
        "--mode",
        choices=["demo"],
        default="demo",
        help="Run mode (currently only 'demo' is supported).",
    )
    parser.add_argument(
        "--max-iters",
        type=int,
        default=_env_int("QA_LIVE_MAX_ITERS", 5),
        help="Maximum loop iterations (default: env QA_LIVE_MAX_ITERS or 5).",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=_env_float("QA_LIVE_LOOP_SLEEP", 1.0),
        help="Seconds to sleep between cycles "
        "(default: env QA_LIVE_LOOP_SLEEP or 1.0).",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=_env_str("QA_LIVE_LOG_LEVEL", "INFO"),
        help="Root log level (default: env QA_LIVE_LOG_LEVEL or INFO).",
    )

    return parser


def configure_logging(log_level: str) -> None:
    # BasicConfig for console output
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(message)s",  # your infra.logging already emits JSON
    )


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    configure_logging(args.log_level)
    logger = get_logger("live.demo")

    logger.info(
        f"Starting live demo loop "
        f"(mode={args.mode}, max_iterations={args.max_iters}, "
        f"sleep={args.sleep_seconds}s)..."
    )

    # Start diagnostics agent (subscribes to EventBus)
    diagnostics = DiagnosticsAgent()
    diagnostics.start()

    if args.mode == "demo":
        signal_engine = DummySignalEngine()
        order_manager = DummyOrderManager()
        safe_broker = DummyBroker()
    else:
        # Future extension: paper/live modes
        raise ValueError(f"Unsupported mode: {args.mode!r}")

    run_live_trading_loop(
        signal_engine=signal_engine,
        order_manager=order_manager,
        safe_broker=safe_broker,
        logger=logger,
        loop_sleep_seconds=args.sleep_seconds,
        max_iterations=args.max_iters,
    )

    logger.info("Live demo finished.")


if __name__ == "__main__":
    main()
