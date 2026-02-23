# path: apps/main_orchestrator.py
from __future__ import annotations

import argparse
import logging
from typing import Any, Optional

from apps.run_live_engine import build_live_context
from orchestrator.trading_orchestrator import (
    TradingOrchestrator,
    OrchestratorConfig,
)


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

def build_logger() -> logging.Logger:
    logger = logging.getLogger("qaai_orchestrator")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


# ---------------------------------------------------------------------------
# Builders – SignalEngine, Broker, OrderManager, Risk, DataUpdater
# ---------------------------------------------------------------------------

def build_signal_engine(mode: str) -> Any:
    logger = build_logger()
    try:
        # TODO: adjust this import if your real SignalEngine lives elsewhere
        from signal_engine.signal_engine import SignalEngine  # type: ignore
    except Exception:
        logger.warning(
            "signal_engine.signal_engine.SignalEngine not available; "
            "falling back to DummySignalEngine (no signals will be produced)."
        )

        class DummySignalEngine:
            def generate_signals(self, *args, **kwargs):
                logger.info("DummySignalEngine.generate_signals() called; returning []")
                return []

        return DummySignalEngine()

    try:
        return SignalEngine(mode=mode)
    except TypeError:
        try:
            return SignalEngine()
        except Exception:
            logger.exception("Failed to instantiate SignalEngine; using DummySignalEngine")

            class DummySignalEngine:
                def generate_signals(self, *args, **kwargs):
                    logger.info(
                        "DummySignalEngine.generate_signals() called after failure; returning []"
                    )
                    return []

            return DummySignalEngine()


class SafeBrokerAdapter:
    """
    Thin wrapper that guarantees a submit_order(...) method exists.

    - If underlying broker has submit_order → forward.
    - Else if it has place_order → forward submit_order → place_order.
    """

    def __init__(self, inner: Any, logger: logging.Logger) -> None:
        self._inner = inner
        self._logger = logger

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def submit_order(self, *args, **kwargs) -> Any:
        if hasattr(self._inner, "submit_order"):
            return self._inner.submit_order(*args, **kwargs)
        if hasattr(self._inner, "place_order"):
            self._logger.debug(
                "SafeBrokerAdapter: forwarding submit_order(...) to place_order(...)"
            )
            return self._inner.place_order(*args, **kwargs)
        raise AttributeError(
            "Underlying broker has neither submit_order nor place_order"
        )


def build_safe_broker(mode: str) -> Any:
    logger = build_logger()

    # Try broker_factory first (like your legacy main orchestrator)
    try:
        from infra.broker_factory import get_broker_adapter  # type: ignore
    except Exception:
        logger.warning(
            "infra.broker_factory.get_broker_adapter not available; "
            "falling back to infra.dhan_adapter.BrokerAdapter if present."
        )
        try:
            from infra.dhan_adapter import BrokerAdapter  # type: ignore
            broker = BrokerAdapter()
        except Exception:
            logger.error(
                "No broker adapter available (neither broker_factory nor dhan_adapter). "
                "Orders will not be routed."
            )
            return None
    else:
        try:
            broker = get_broker_adapter(mode=mode)
        except TypeError:
            logger.debug(
                "get_broker_adapter(mode=...) signature not supported; retrying without mode"
            )
            broker = get_broker_adapter()

    # Wrap in SafeBrokerAdapter if we have something
    if broker is None:
        logger.error("Broker adapter is None; orders will not be routed.")
        return None

    return SafeBrokerAdapter(broker, logger=logger)


class FlexibleOrderManager:
    """
    Adapter around the real OrderManager that accepts "rich" create_order(...)
    calls from ExecutionEngine and translates them to the canonical
    signature used by your OrderManager:

        create_order(symbol, side, quantity, price, meta=None)

    All extra args/kwargs are merged into meta.
    """

    def __init__(self, inner: Any, logger: logging.Logger) -> None:
        self._inner = inner
        self._logger = logger

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def create_order(self, *args, **kwargs) -> Any:
        meta = kwargs.pop("meta", {}) or {}

        # Merge all remaining kwargs into meta (sl, tp, strategy_id, etc.)
        for k in list(kwargs.keys()):
            meta.setdefault(k, kwargs.pop(k))

        # Positional extraction
        if len(args) >= 4:
            symbol, side, quantity, price = args[:4]
            extra_positional = args[4:]
            if extra_positional:
                # Keep extra positional info in meta for debugging
                meta.setdefault("extra_args", extra_positional)
        else:
            symbol = kwargs.pop("symbol", "MOCK")
            side = kwargs.pop("side", "BUY")
            quantity = kwargs.pop("quantity", 1)
            price = kwargs.pop("price", 0.0)

        try:
            return self._inner.create_order(symbol, side, quantity, price, meta=meta)
        except TypeError:
            # Fallback in case the underlying API is slightly different
            self._logger.debug(
                "FlexibleOrderManager: inner.create_order signature mismatch; "
                "retrying positional-only call."
            )
            return self._inner.create_order(symbol, side, quantity, price)


def build_order_manager(mode: str) -> Any:
    logger = build_logger()

    try:
        from qaai_system.execution.order_manager import OrderManager  # type: ignore
    except Exception:
        logger.warning(
            "execution.order_manager.OrderManager not available; "
            "using simple in-memory fallback OrderManager."
        )

        class FallbackOrderManager:
            def __init__(self, *args, **kwargs) -> None:
                self._orders = []

            def create_order(self, **fields) -> str:
                oid = f"order_{len(self._orders) + 1}"
                payload = {"order_id": oid, **fields}
                self._orders.append(payload)
                logger.info("FallbackOrderManager created order %s", payload)
                return oid

            def get_all_orders(self):
                return list(self._orders)

        return FallbackOrderManager()

    # Optional TradeClassifier
    classifier: Optional[Any]
    try:
        from qaai_system.execution.trade_classifier import TradeClassifier  # type: ignore
        classifier = TradeClassifier()
    except Exception:
        logger.info(
            "execution.trade_classifier.TradeClassifier not available; continuing without."
        )
        classifier = None

    broker = build_safe_broker(mode=mode)

    # Instantiate the real OrderManager
    if classifier is not None:
        try:
            om = OrderManager(broker_adapter=broker, classifier=classifier)
        except TypeError:
            logger.debug(
                "OrderManager(broker_adapter=..., classifier=...) not supported; "
                "retrying without classifier."
            )
            om = OrderManager(broker_adapter=broker)
    else:
        try:
            om = OrderManager(broker_adapter=broker)
        except TypeError:
            logger.debug(
                "OrderManager(broker_adapter=...) not supported; retrying with positional broker."
            )
            om = OrderManager(broker)

    # Wrap it in the flexible adapter used only by CLI orchestrator
    return FlexibleOrderManager(om, logger=logger)


def build_risk_engine(mode: str) -> Optional[Any]:
    logger = build_logger()

    try:
        from risk.risk_engine import RiskEngine  # type: ignore
        from risk.risk_limits import RiskLimits  # type: ignore
    except Exception:
        logger.info(
            "risk.risk_engine / risk.risk_limits not available; "
            "running without orchestrator-level RiskEngine."
        )
        return None

    try:
        if hasattr(RiskLimits, "from_env"):
            limits = RiskLimits.from_env(mode=mode)  # type: ignore[arg-type]
        elif hasattr(RiskLimits, "from_mode"):
            limits = RiskLimits.from_mode(mode=mode)  # type: ignore[arg-type]
        else:
            limits = RiskLimits()  # type: ignore[call-arg]
    except Exception:
        logger.exception("Failed to construct RiskLimits; falling back to defaults.")
        try:
            limits = RiskLimits()  # type: ignore[call-arg]
        except Exception:
            limits = None

    try:
        if limits is not None:
            return RiskEngine(limits=limits, logger=logger)
        return RiskEngine(logger=logger)  # type: ignore[call-arg]
    except TypeError:
        try:
            return RiskEngine()
        except Exception:
            logger.exception("Failed to construct RiskEngine; disabling orchestrator risk.")
            return None


def build_data_updater(mode: str) -> Optional[Any]:
    logger = build_logger()

    try:
        from auto_updater import AutoUpdater  # type: ignore
    except Exception:
        logger.info(
            "auto_updater.AutoUpdater not available; orchestrator will run "
            "without a central data_updater."
        )
        return None

    try:
        return AutoUpdater(mode=mode)
    except TypeError:
        logger.debug("AutoUpdater(mode=...) not supported; retrying without mode.")
        try:
            return AutoUpdater()
        except Exception:
            logger.exception("Failed to construct AutoUpdater; disabling data_updater.")
            return None


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="QA AI Trading Orchestrator entrypoint",
    )
    parser.add_argument(
        "--mode",
        choices=["backtest", "paper", "live"],
        default="paper",
        help="Trading mode to start the orchestrator in.",
    )
    parser.add_argument(
        "--cycle-interval",
        type=float,
        default=1.0,
        help="Seconds between orchestrator cycles.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Optional max cycles before exit (useful for smoke tests).",
    )

    args = parser.parse_args()
    mode = args.mode

    logger = build_logger()
    logger.info("Starting main orchestrator", extra={"mode": mode})

    # --- Build core stack pieces ---
    signal_engine = build_signal_engine(mode=mode)
    order_manager = build_order_manager(mode=mode)
    safe_broker = build_safe_broker(mode=mode)
    risk_engine = build_risk_engine(mode=mode)
    data_updater = build_data_updater(mode=mode)

    # --- Build Phase 6 live context (engine, tracker, etc.) ---
    ctx = build_live_context(
        signal_engine=signal_engine,
        order_manager=order_manager,
        safe_broker=safe_broker,
        logger=logger,
        risk_engine=risk_engine,
    )

    # --- Build Phase 7 orchestrator ---
    orchestrator = TradingOrchestrator(
        engine=ctx.engine,
        position_tracker=ctx.position_tracker,
        order_manager=order_manager,
        risk_engine=risk_engine,
        data_updater=data_updater,
        logger=logger,
        mode=mode,
        config=OrchestratorConfig(cycle_interval=args.cycle_interval),
    )

    if args.max_iterations is not None:
        logger.info("Running orchestrator for %s iterations", args.max_iterations)
        for _ in range(args.max_iterations):
            if orchestrator._should_stop():
                break
            orchestrator.sync_time()
            if data_updater is not None and hasattr(data_updater, "refresh"):
                try:
                    data_updater.refresh()
                except Exception:
                    logger.exception("data_updater.refresh() failed")

            orchestrator.run_cycle()
        logger.info("main_orchestrator: completed fixed-iteration run")
    else:
        orchestrator.start()


if __name__ == "__main__":
    main()
