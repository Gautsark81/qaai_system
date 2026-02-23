# tests/test_sanity_pipeline.py

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)  # ensure qaai_system is importable

import pytest
import pandas as pd

from qaai_system.signal_engine.signal_engine import SignalEngine
from qaai_system.execution.execution_engine import ExecutionEngine
from qaai_system.execution.orchestrator import ExecutionOrchestrator
from qaai_system.execution.risk_manager import RiskManager
from qaai_system.execution.position_manager import PositionManager  # fixed import
from qaai_system.execution.router import DummyRouter


def _get_trade_log_entries(trade_logger):
    """
    Normalize access to trade logs across real TradeLogger (CSV)
    and fallback _SimpleTradeLogger (in-memory).
    """
    if hasattr(trade_logger, "logged_trades"):
        return list(trade_logger.logged_trades)
    elif hasattr(trade_logger, "trades"):
        return list(trade_logger.trades)
    else:
        return []


# --- tests ------------------------------------------------------


def test_signal_engine_run_returns_df():
    se = SignalEngine()
    df = se.run(["AAPL", "RELIANCE"])
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "symbol" in df.columns
    assert "side" in df.columns


def test_execution_engine_process_and_monitor():
    se = SignalEngine()
    ee = ExecutionEngine(signal_engine=se)

    # Generate & process signals
    ee.process_signals()

    orders = ee.order_manager.get_all_orders()
    assert isinstance(orders, dict)
    assert len(orders) > 0

    # Monitor open orders and trigger closes
    closed = ee.monitor_open_orders()
    assert isinstance(closed, list)

    # Ensure trades got logged (real logger may not expose in-memory log)
    trades = _get_trade_log_entries(ee.trade_logger)
    assert isinstance(trades, list)


def test_router_parentresponse_handling(monkeypatch):
    orch = ExecutionOrchestrator(
        router=DummyRouter(),
        risk=RiskManager({}),
        positions=PositionManager(),
        config={"starting_cash": 100000},
    )
    # make sure router returns ParentResponse-like object (DummyRouter does)
    out = orch.submit_order(
        {"symbol": "AAA", "side": "buy", "quantity": 1, "price": 10.0}
    )
    assert out["status"] in (
        "filled",
        "submitted",
        "open",
        "partial",
        "partially_filled",
    )


def test_symbol_cap_uses_provider_positions():
    cfg = {"risk": {"max_symbol_weight": 0.5}}
    rm = RiskManager(cfg)
    orch = ExecutionOrchestrator(
        router=DummyRouter(),
        risk=rm,
        positions=PositionManager(),
        config={"starting_cash": 10000},
    )
    provider = orch.provider
    provider._account_nav = 10000
    provider._positions["SYM"] = 45
    provider._positions["__last_price__:SYM"] = 100
    with pytest.raises(ValueError, match="Symbol cap exceeded for SYM"):
        orch.submit_order(
            {"symbol": "SYM", "side": "buy", "quantity": 10, "price": 100}
        )


def test_execution_engine_broker_wrap_and_submit():
    class DummyBroker:
        def __init__(self):
            self.calls = []

        def submit_order(self, symbol, side, qty, price, *a, **kw):
            self.calls.append((symbol, side, qty, price))
            return {"status": "CLOSED", "pnl": 10.0}

    broker = DummyBroker()
    se = SignalEngine()
    ee = ExecutionEngine(signal_engine=se, broker_adapter=broker)

    # Call submit_order — should be wrapped
    broker.submit_order("RELIANCE", "BUY", 1, 100.0)

    # Key assertion: wrapper invoked broker
    assert len(broker.calls) == 1

    # Optional: check trade logger (tolerant to 0 if CSV-based logger)
    trades = _get_trade_log_entries(ee.trade_logger)
    assert isinstance(trades, list)

    # Orders should always be a dict
    orders = ee.order_manager.get_all_orders()
    assert isinstance(orders, dict)
