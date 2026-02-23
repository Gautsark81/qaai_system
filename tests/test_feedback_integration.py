# tests/test_feedback_integration.py
from unittest.mock import MagicMock
from qaai_system.execution.execution_engine import ExecutionEngine
from qaai_system.signal_engine.signal_engine import SignalEngine


def test_on_fill_calls_register(monkeypatch, tmp_path):
    # create a dummy SignalEngine with a spy register_trade_result
    se = SignalEngine()
    se.register_trade_result = MagicMock()

    # create ExecutionEngine with mock broker and our signal engine
    ee = ExecutionEngine(broker_adapter=None, signal_engine=se)

    fill_event = {
        "trade_id": "T1",
        "symbol": "AAA",
        "filled_qty": 10,
        "avg_fill_price": 100.0,
        "side": "BUY",
        "status": "CLOSED",
        "close_reason": "TP",
        "pnl": 50.0,
        "strategy_id": "alpha_v1",
    }

    ee.on_fill(fill_event)

    # wait a small moment for thread to execute (if you used threads)
    import time

    time.sleep(0.1)

    # assert that register_trade_result was called
    se.register_trade_result.assert_called()
    args, kwargs = se.register_trade_result.call_args
    assert args[0] == "T1"
    assert args[1] == 50.0
    assert args[2] is False  # sl_hit
    assert args[3] is True  # tp_hit
    assert isinstance(args[4], dict) or args[4] is None
