from __future__ import annotations

"""
Trading Orchestrator v1 (Autonomous Loop)

This module defines TradingOrchestrator, the core loop that coordinates:

    - data_updater.refresh()
    - ExecutionEngine.process_signals()
    - optional ExecutionEngine.monitor_orders()
    - RiskEngine kill switch / panic checks
    - per-cycle metrics and structured logging

It is intentionally robust and test-friendly:
- All dependencies are injected (engine, risk_engine, etc.)
- Metrics/logging sinks are best-effort and never crash the app
"""

import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional

from qaai_system.execution.execution_engine import ExecutionEngine
from portfolio.position_tracker import PositionTracker
from risk.risk_engine import RiskEngine

# ---------------------------------------------------------------------------
# Optional Phase 8 observability integration
# ---------------------------------------------------------------------------

try:  # optional structured logging
    from infra.structured_logger import log_structured as _log_structured
except Exception:
    def _log_structured(logger: Any, level: str, event: str, **fields: Any) -> None:
        """Fallback structured logger: log as simple text."""
        try:
            payload = {"event": event, **fields}
            logger.info("%s %s", event, json.dumps(payload))
        except Exception:
            try:
                logger.info("%s %s", event, fields)
            except Exception:
                pass


try:  # optional metrics sink
    from qaai_system.analytics.metrics.cycle_metrics import record_cycle_metrics as _record_cycle_metrics
except Exception:
    def _record_cycle_metrics(metrics: Dict[str, Any]) -> None:
        """Fallback metrics sink: no-op."""
        return


__all__ = ["TradingMode", "OrchestratorConfig", "TradingOrchestrator"]


class TradingMode(str, Enum):
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


@dataclass
class OrchestratorConfig:
    """
    Configuration for TradingOrchestrator.

    Attributes
    ----------
    cycle_interval : float
        Time to sleep between cycles, in seconds.
    """

    cycle_interval: float = 1.0


class TradingOrchestrator:
    """
    Central trading orchestrator.

    This class coordinates:
        - data_updater.refresh()        (if provided)
        - ExecutionEngine.process_signals()
        - optional ExecutionEngine.monitor_orders()
        - RiskEngine kill switch checks
        - Per-cycle health metrics logging
        - Optional panic-handling (flatten, kill-switch)
    """

    def __init__(
        self,
        engine: ExecutionEngine,
        position_tracker: PositionTracker,
        order_manager: Any,
        risk_engine: Optional[RiskEngine],
        data_updater: Optional[Any],
        logger: Any,
        *,
        mode: str = "paper",
        config: Optional[OrchestratorConfig] = None,
        stop_event: Optional[Any] = None,
        on_cycle_start: Optional[Callable[["TradingOrchestrator", Dict[str, Any]], None]] = None,
        on_cycle_end: Optional[Callable[["TradingOrchestrator", Dict[str, Any]], None]] = None,
        on_panic: Optional[Callable[["TradingOrchestrator", str, Dict[str, Any]], None]] = None,
    ) -> None:
        self.engine = engine
        self.position_tracker = position_tracker
        self.order_manager = order_manager
        self.risk_engine = risk_engine
        self.data_updater = data_updater
        self.logger = logger

        self.config = config or OrchestratorConfig()
        self.mode: TradingMode = TradingMode(mode)

        self._stop_event = stop_event  # e.g. threading.Event
        self._local_stop_flag = False

        # Hooks
        self.on_cycle_start = on_cycle_start
        self.on_cycle_end = on_cycle_end
        self.on_panic = on_panic

        # last metrics snapshot (optional introspection)
        self.last_cycle_metrics: Dict[str, Any] = {}

        # init log
        try:
            payload = {
                "event": "ORCHESTRATOR_INIT",
                "mode": self.mode.value,
                "cycle_interval": self.config.cycle_interval,
            }
            self.logger.info("ORCHESTRATOR_INIT %s", json.dumps(payload))
        except Exception:
            try:
                self.logger.info(
                    "TradingOrchestrator initialized mode=%s interval=%s",
                    self.mode.value,
                    self.config.cycle_interval,
                )
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Mode control
    # ------------------------------------------------------------------

    def set_mode(self, mode: str) -> None:
        """
        Change orchestrator mode at runtime.

        Parameters
        ----------
        mode : {"backtest","paper","live"}
        """
        self.mode = TradingMode(mode)
        try:
            payload = {"event": "MODE_CHANGE", "mode": self.mode.value}
            self.logger.info("MODE_CHANGE %s", json.dumps(payload))
        except Exception:
            try:
                self.logger.info("Mode changed to %s", self.mode.value)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Lifecycle: start / stop / sync_time
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Start the main loop (blocking).

        Loop:
            sync_time()
            data_updater.refresh()
            run_cycle()
            sleep(config.cycle_interval)
        """
        self._local_stop_flag = False
        try:
            payload = {
                "event": "ORCHESTRATOR_START",
                "mode": self.mode.value,
            }
            self.logger.info("ORCHESTRATOR_START %s", json.dumps(payload))
        except Exception:
            try:
                self.logger.info("TradingOrchestrator starting main loop")
            except Exception:
                pass

        while not self._should_stop():
            self.sync_time()

            # Refresh market data / LTP cache, etc.
            if self.data_updater is not None and hasattr(self.data_updater, "refresh"):
                try:
                    self.data_updater.refresh()
                except Exception:
                    self.logger.exception("data_updater.refresh() failed")

            # Run one trading cycle
            self.run_cycle()

            time.sleep(self.config.cycle_interval)

        # Graceful shutdown flush hook
        self._log_open_positions_summary()
        try:
            payload = {
                "event": "ORCHESTRATOR_STOP",
                "mode": self.mode.value,
            }
            self.logger.info("ORCHESTRATOR_STOP %s", json.dumps(payload))
        except Exception:
            try:
                self.logger.info("TradingOrchestrator stopped main loop")
            except Exception:
                pass

    def stop(self) -> None:
        """
        Request the orchestrator to stop at the next cycle boundary.

        Works with or without an external stop_event.
        """
        self._local_stop_flag = True
        if self._stop_event is not None and hasattr(self._stop_event, "set"):
            self._stop_event.set()

    def _should_stop(self) -> bool:
        if self._local_stop_flag:
            return True
        if self._stop_event is not None and hasattr(self._stop_event, "is_set"):
            return bool(self._stop_event.is_set())
        return False

    def sync_time(self) -> None:
        """
        Placeholder for time sync logic.

        In the future you can add:
        - Exchange clock sync
        - NTP checks
        - Time drift alarms
        """
        return

    # ------------------------------------------------------------------
    # Core per-cycle logic
    # ------------------------------------------------------------------

    def run_cycle(self) -> None:
        """
        Run a single orchestrator cycle.

        Responsibilities:
            - check RiskEngine kill switch
            - run appropriate mode branch (backtest / paper / live)
            - collect metrics (latency, signals, orders, risk rejects)
            - log metrics in a structured way
            - fire on_cycle_start / on_cycle_end hooks
        """
        cycle_start = time.perf_counter()
        metrics: Dict[str, Any] = {
            "mode": self.mode.value,
            "timestamp": time.time(),
        }

        # Hook: cycle start
        if self.on_cycle_start is not None:
            try:
                self.on_cycle_start(self, metrics)
            except Exception:
                self.logger.exception("on_cycle_start hook failed")

        # Risk kill switch
        if self._risk_kill_switch_active():
            metrics["kill_switch_active"] = True
            self._log_cycle_metrics(cycle_start, metrics)
            if self.on_cycle_end is not None:
                try:
                    self.on_cycle_end(self, metrics)
                except Exception:
                    self.logger.exception("on_cycle_end hook failed")
            self.last_cycle_metrics = dict(metrics)
            return

        # Panic detection via RiskEngine (if implemented)
        if self._risk_catastrophic():
            self._handle_panic("risk_engine_catastrophic", metrics)
            self.last_cycle_metrics = dict(metrics)
            return

        try:
            if self.mode is TradingMode.BACKTEST:
                self._run_backtest_cycle(metrics)
            else:
                self._run_live_or_paper_cycle(metrics)
        except Exception:
            self.logger.exception("run_cycle: unhandled exception in trading logic")

        # Final metrics log + hooks
        self._log_cycle_metrics(cycle_start, metrics)

        if self.on_cycle_end is not None:
            try:
                self.on_cycle_end(self, metrics)
            except Exception:
                self.logger.exception("on_cycle_end hook failed")

        self.last_cycle_metrics = dict(metrics)

    # ------------------------------------------------------------------
    # Internal helpers for cycle logic
    # ------------------------------------------------------------------

    def _run_backtest_cycle(self, metrics: Dict[str, Any]) -> None:
        """
        Backtest mode: drive historical data into SignalEngine only.
        """
        engine = self.engine
        signal_engine = getattr(engine, "signal_engine", None)

        num_signals_before = self._get_signal_count(signal_engine)
        engine.process_signals()
        num_signals_after = self._get_signal_count(signal_engine)

        metrics["num_signals"] = max(0, (num_signals_after or 0) - (num_signals_before or 0))
        metrics["num_orders"] = 0
        metrics["num_rejected_by_risk"] = self._get_risk_rejected_count()

    def _run_live_or_paper_cycle(self, metrics: Dict[str, Any]) -> None:
        """
        Live / paper modes: full signals → execution → orders pipeline.
        """
        engine = self.engine
        signal_engine = getattr(engine, "signal_engine", None)

        num_signals_before = self._get_signal_count(signal_engine)
        num_orders_before = self._get_order_count()

        engine.process_signals()

        # Only call monitor_orders if it exists (dummy engine in tests has it).
        if hasattr(engine, "monitor_orders"):
            try:
                engine.monitor_orders()
            except Exception:
                self.logger.exception("engine.monitor_orders() failed")

        num_signals_after = self._get_signal_count(signal_engine)
        num_orders_after = self._get_order_count()

        metrics["num_signals"] = max(0, (num_signals_after or 0) - (num_signals_before or 0))
        metrics["num_orders"] = max(0, num_orders_after - num_orders_before)
        metrics["num_rejected_by_risk"] = self._get_risk_rejected_count()

    # ------------------------------------------------------------------
    # Metrics & logging helpers
    # ------------------------------------------------------------------

    def _log_cycle_metrics(self, cycle_start: float, metrics: Dict[str, Any]) -> None:
        """
        Compute latency and log metrics as a structured event.

        - Adds `cycle_latency_ms` to metrics
        - Emits a structured log via _log_structured(...)
        - Persists metrics via _record_cycle_metrics(...)
        """
        latency_ms = (time.perf_counter() - cycle_start) * 1000.0
        metrics["cycle_latency_ms"] = latency_ms

        # Best-effort: persist metrics to the metrics sink
        try:
            _record_cycle_metrics(metrics)
        except Exception:
            try:
                self.logger.exception("Failed to record cycle metrics")
            except Exception:
                pass

        # Structured log: TRADING_CYCLE
        try:
            _log_structured(
                self.logger,
                level="INFO",
                event="TRADING_CYCLE",
                mode=self.mode.value,
                **metrics,
            )
        except Exception:
            # Fallback to previous behaviour for robustness
            try:
                payload = {
                    "event": "TRADING_CYCLE",
                    "metrics": metrics,
                }
                self.logger.info("TRADING_CYCLE %s", json.dumps(payload))
            except Exception:
                try:
                    self.logger.info("TRADING_CYCLE metrics=%s", metrics)
                except Exception:
                    pass

    def _get_signal_count(self, signal_engine: Any) -> Optional[int]:
        """
        Best-effort way to get number of signals produced in the last step.
        """
        if signal_engine is None:
            return None

        if hasattr(signal_engine, "last_num_signals"):
            try:
                return int(signal_engine.last_num_signals)  # type: ignore[arg-type]
            except Exception:
                pass

        for attr in ("last_signals", "signals", "_last_signals"):
            if hasattr(signal_engine, attr):
                obj = getattr(signal_engine, attr)
                try:
                    return len(obj)
                except Exception:
                    continue

        return None

    def _get_order_count(self) -> int:
        """
        Best-effort way to count orders from the OrderManager.
        """
        om = self.order_manager
        if om is None:
            return 0

        if hasattr(om, "get_all_orders"):
            try:
                orders = om.get_all_orders()
                return len(orders)
            except Exception:
                pass

        if hasattr(om, "orders"):
            try:
                return len(om.orders)
            except Exception:
                pass

        return 0

    def _get_risk_rejected_count(self) -> int:
        """
        Best-effort way to get number of orders rejected by risk on last cycle.
        """
        re = self.risk_engine
        if re is None:
            return 0

        for attr in ("last_rejected", "last_rejected_count"):
            if hasattr(re, attr):
                try:
                    return int(getattr(re, attr))
                except Exception:
                    continue

        return 0

    # ------------------------------------------------------------------
    # Risk & panic helpers
    # ------------------------------------------------------------------

    def _risk_kill_switch_active(self) -> bool:
        """
        Check if RiskEngine kill switch is active.
        """
        re = self.risk_engine
        if re is None:
            return False
        try:
            return bool(getattr(re, "kill_switch", False))
        except Exception:
            return False

    def _risk_catastrophic(self) -> bool:
        """
        Check if RiskEngine declares a catastrophic condition.

        Looks for a boolean method:
            risk_engine.is_catastrophic()
        """
        re = self.risk_engine
        if re is None:
            return False

        if hasattr(re, "is_catastrophic"):
            try:
                return bool(re.is_catastrophic())
            except Exception:
                return False

        return False

    def _handle_panic(self, reason: str, metrics: Dict[str, Any]) -> None:
        """
        Panic path:
            - set risk_engine.kill_switch = True (if available)
            - attempt to close all positions
            - log PANIC_SHUTDOWN event
            - invoke on_panic hook
            - stop orchestrator
        """
        metrics["panic_reason"] = reason

        # Set kill switch
        if self.risk_engine is not None:
            try:
                setattr(self.risk_engine, "kill_switch", True)
            except Exception:
                pass

        # Attempt to close all positions via OrderManager (if supported)
        om = self.order_manager
        closed_positions = False
        for method_name in ("close_all_positions", "flatten_all", "flatten"):
            if om is not None and hasattr(om, method_name):
                try:
                    getattr(om, method_name)()
                    closed_positions = True
                    break
                except Exception:
                    self.logger.exception("panic: %s() failed", method_name)

        payload = {
            "event": "PANIC_SHUTDOWN",
            "reason": reason,
            "closed_positions": closed_positions,
            "mode": self.mode.value,
        }
        try:
            self.logger.error("PANIC_SHUTDOWN %s", json.dumps(payload))
        except Exception:
            try:
                self.logger.error("PANIC_SHUTDOWN payload=%s", payload)
            except Exception:
                pass

        if self.on_panic is not None:
            try:
                self.on_panic(self, reason, metrics)
            except Exception:
                self.logger.exception("on_panic hook failed")

        # Request stop after panic
        self.stop()

    # ------------------------------------------------------------------
    # Shutdown helpers
    # ------------------------------------------------------------------

    def _log_open_positions_summary(self) -> None:
        """
        Optional open-positions summary on graceful shutdown.
        """
        pt = self.position_tracker
        if pt is None:
            return

        positions = None
        if hasattr(pt, "get_open_positions"):
            try:
                positions = pt.get_open_positions()
            except Exception:
                positions = None

        payload = {
            "event": "OPEN_POSITIONS_SUMMARY",
            "positions": positions,
            "mode": self.mode.value,
        }
        try:
            self.logger.info("OPEN_POSITIONS_SUMMARY %s", json.dumps(payload))
        except Exception:
            try:
                self.logger.info("OPEN_POSITIONS_SUMMARY payload=%s", payload)
            except Exception:
                pass
