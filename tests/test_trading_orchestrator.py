# path: tests/test_trading_orchestrator.py
from __future__ import annotations

import time

import pytest

from qaai_system.orchestrator.trading_orchestrator import (
    TradingOrchestrator,
    OrchestratorConfig,
    TradingMode,
)


# ---------------------------------------------------------------------------
# Dummy collaborators for orchestrator tests
# ---------------------------------------------------------------------------


class DummyLogger:
    def info(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def debug(self, *args, **kwargs):
        pass

    def exception(self, *args, **kwargs):
        pass


class DummySignalEngine:
    def __init__(self):
        self.signals = []  # orchestrator uses len() via _get_signal_count


class DummyOrderManager:
    def __init__(self):
        self.orders = []
        self.close_all_positions_called = False

    def get_all_orders(self):
        return self.orders

    def close_all_positions(self):
        # used in panic path
        self.close_all_positions_called = True


class DummyPositionTracker:
    def __init__(self):
        self._open_positions = {}

    def get_open_positions(self):
        return self._open_positions

    def log_snapshot(self, equity=None, cash=None):
        # orchestrator doesn't directly call this, but Phase 6 helpers do.
        pass


class DummyRiskEngine:
    def __init__(self):
        self.kill_switch = False
        self.last_rejected = 0
        self._catastrophic = False

    def is_catastrophic(self) -> bool:
        return self._catastrophic


class DummyExecutionEngine:
    """
    Minimal stub for ExecutionEngine used by TradingOrchestrator.

    - process_signals: appends a fake signal
    - monitor_orders: appends a fake order
    """

    def __init__(self, signal_engine: DummySignalEngine, order_manager: DummyOrderManager):
        self.signal_engine = signal_engine
        self.order_manager = order_manager

    def process_signals(self):
        # Produce exactly one new signal each time
        self.signal_engine.signals.append(
            {"id": len(self.signal_engine.signals) + 1}
        )

    def monitor_orders(self):
        # Create one new order per cycle
        self.order_manager.orders.append(
            {"id": len(self.order_manager.orders) + 1}
        )


class DummyDataUpdater:
    def __init__(self):
        self.refresh_count = 0

    def refresh(self):
        self.refresh_count += 1


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def _build_orchestrator(
    mode: str = "live",
    risk_engine: DummyRiskEngine | None = None,
) -> tuple[TradingOrchestrator, DummyOrderManager, DummyRiskEngine]:
    """
    Helper to create a minimally-wired orchestrator with dummies.
    """
    logger = DummyLogger()
    signal_engine = DummySignalEngine()
    order_manager = DummyOrderManager()
    position_tracker = DummyPositionTracker()
    risk_engine = risk_engine or DummyRiskEngine()
    engine = DummyExecutionEngine(signal_engine=signal_engine, order_manager=order_manager)
    data_updater = DummyDataUpdater()

    orchestrator = TradingOrchestrator(
        engine=engine,
        position_tracker=position_tracker,
        order_manager=order_manager,
        risk_engine=risk_engine,
        data_updater=data_updater,
        logger=logger,
        mode=mode,
        config=OrchestratorConfig(cycle_interval=0.0),
    )
    return orchestrator, order_manager, risk_engine


def test_orchestrator_single_cycle_creates_one_order():
    """
    Single-cycle test:

    - Mock SignalEngine emits one signal via DummyExecutionEngine
    - ensure OrderManager has 1 new order after run_cycle()
    """
    orchestrator, order_manager, _ = _build_orchestrator(mode="live")

    assert len(order_manager.orders) == 0
    orchestrator.run_cycle()
    assert len(order_manager.orders) == 1


def test_orchestrator_kill_switch_blocks_orders():
    """
    Kill-switch test:

    - risk_engine.kill_switch=True
    - run_cycle() should NOT create new orders.
    """
    risk_engine = DummyRiskEngine()
    risk_engine.kill_switch = True

    orchestrator, order_manager, _ = _build_orchestrator(
        mode="live", risk_engine=risk_engine
    )

    assert len(order_manager.orders) == 0
    orchestrator.run_cycle()
    # No orders should be produced when kill switch is active
    assert len(order_manager.orders) == 0


def test_orchestrator_mode_switch_updates_mode_enum():
    """
    Mode test (lightweight):

    - create orchestrator in 'paper' mode
    - switch to 'live'
    - ensure mode enum updates correctly
    """
    orchestrator, _, _ = _build_orchestrator(mode="paper")
    assert orchestrator.mode == TradingMode.PAPER

    orchestrator.set_mode("live")
    assert orchestrator.mode == TradingMode.LIVE


def test_orchestrator_panic_triggers_kill_switch_and_flatten():
    """
    Panic path test:

    - risk_engine.is_catastrophic() returns True
    - orchestrator.run_cycle() should:
        * set risk_engine.kill_switch = True
        * attempt to close all positions via OrderManager
        * request orchestrator stop (local flag)
    """
    risk_engine = DummyRiskEngine()
    risk_engine._catastrophic = True  # trigger panic

    orchestrator, order_manager, risk_engine = _build_orchestrator(
        mode="live", risk_engine=risk_engine
    )

    # Before panic
    assert risk_engine.kill_switch is False
    assert order_manager.close_all_positions_called is False

    orchestrator.run_cycle()

    # After panic
    assert risk_engine.kill_switch is True
    assert order_manager.close_all_positions_called is True
    # _local_stop_flag should be set by orchestrator.stop()
    assert orchestrator._should_stop() is True
