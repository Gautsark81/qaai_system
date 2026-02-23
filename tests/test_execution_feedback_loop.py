import pytest
from unittest.mock import MagicMock
from qaai_system.execution.execution_engine import ExecutionEngine


class DummyBroker:
    """A simple paper broker that calls back fills instantly."""

    def __init__(self):
        self._fill_callback = None

    def set_fill_callback(self, cb):
        self._fill_callback = cb

    def submit_order(self, symbol, side, qty, price):
        # Simulate instant fill
        fill_event = {
            "trade_id": f"{symbol}_TEST_1",
            "symbol": symbol,
            "filled_qty": qty,
            "avg_fill_price": price,
            "side": side.upper(),
            "status": "CLOSED",
            "close_reason": "TP",
            "pnl": 123.45,
            "strategy_id": "test_strategy",
        }
        if self._fill_callback:
            self._fill_callback(fill_event)
        return {"status": "closed", "fill_price": price, "filled_quantity": qty}

    def check_stop_loss_take_profit(self, order, current_price, config):
        return None


@pytest.fixture
def dummy_engine():
    signal_engine = MagicMock()
    broker = DummyBroker()

    # Pass in only required deps for our test
    engine = ExecutionEngine(
        signal_provider=None,
        order_manager=MagicMock(),
        risk_manager=None,
        trade_logger=None,
        broker_adapter=broker,
        config={"sl_tp": {"enabled": False}},
        signal_engine=signal_engine,
    )
    return engine, broker, signal_engine


def test_feedback_loop_called(dummy_engine):
    engine, broker, signal_engine = dummy_engine

    # Place a simulated order — will trigger DummyBroker.submit_order → on_fill
    broker.submit_order("RELIANCE", "buy", 10, 2500.0)

    # Feedback loop should have been called once
    assert signal_engine.register_trade_result.call_count == 1

    # Check arguments passed
    args, kwargs = signal_engine.register_trade_result.call_args
    trade_id, pnl, sl_hit, tp_hit, meta = args
    assert trade_id.startswith("RELIANCE_")
    assert pnl == 123.45
    assert sl_hit is False
    assert tp_hit is True
    assert meta["symbol"] == "RELIANCE"
    assert meta["side"] == "BUY"
    assert meta["filled_qty"] == 10
    assert meta["avg_price"] == 2500.0
