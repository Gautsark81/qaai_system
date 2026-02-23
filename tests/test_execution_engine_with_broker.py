# path: tests/test_execution_engine_with_broker.py

import pandas as pd

from qaai_system.execution.execution_engine import ExecutionEngine
from qaai_system.execution.order_manager import OrderManager
from qaai_system.broker.dhan_safe_client import DhanSafeClient, DhanSafeConfig


class DummyRawDhan:
    """Very simple raw client that just records calls."""

    def __init__(self):
        self.place_orders = []

    def place_order(self, **kwargs):
        # Record whatever DhanSafeClient mapped into
        self.place_orders.append(kwargs)
        return {
            "dhan_order_id": f"DO_{len(self.place_orders)}",
            "order_status": "SUCCESS",
        }


class DummySignalEngine:
    """Minimal signal engine returning a single BUY signal row."""

    def run(self, symbols):
        return pd.DataFrame(
            [
                {
                    "symbol": "NIFTY24FEBFUT",
                    "side": "BUY",
                    "price": 100.0,
                    "sl_scaled": 99.0,
                    "tp_scaled": 101.0,
                    "position_size": 1,
                    "strategy_id": "unit-test-strategy",
                }
            ]
        )

    def register_trade_result(self, trade_id, pnl, sl_hit, tp_hit, meta):
        # For now, just a stub; assertions could be added later
        pass


class DummyBrokerForOrderManager:
    """Broker used only by OrderManager; uses submit_order API."""

    def __init__(self):
        self.calls = []

    def submit_order(self, symbol, side, quantity, price, order_meta=None):
        self.calls.append(
            {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": price,
                "order_meta": order_meta or {},
            }
        )
        return {
            "order_id": f"OM_{len(self.calls)}",
            "status": "open",
            "fill_price": price,
        }


def build_safe_broker():
    cfg = DhanSafeConfig(client_id="x", access_token="y")
    raw = DummyRawDhan()
    safe = DhanSafeClient(config=cfg, raw_client=raw)
    return safe, raw


def test_execution_engine_sends_orders_to_broker_and_order_manager():
    signal_engine = DummySignalEngine()

    # OrderManager needs a broker with submit_order(...)
    om_broker = DummyBrokerForOrderManager()
    order_manager = OrderManager(broker=om_broker)

    # ExecutionEngine uses DhanSafeClient -> DummyRawDhan (place_order)
    broker, raw = build_safe_broker()

    config = {"exec_mode": "live"}
    ee = ExecutionEngine(
        signal_engine=signal_engine,
        order_manager=order_manager,
        broker_adapter=broker,
        config=config,
    )

    ee.process_signals()

    # Assert local order created in OrderManager (ignore synthetic placeholders)
    orders = order_manager.get_all_orders()
    assert isinstance(orders, dict)
    real_orders = {k: v for k, v in orders.items() if not k.startswith("__")}
    assert real_orders, "Expected at least one real order in OrderManager"

    oid, o = list(real_orders.items())[0]
    assert o["symbol"] == "NIFTY24FEBFUT"
    assert o["side"].upper() == "BUY"

    # Assert broker (via DhanSafeClient) received a place_order
    assert len(raw.place_orders) == 1
    call = raw.place_orders[0]
    assert call["symbol"] == "NIFTY24FEBFUT"
    assert call["transaction_type"] == "BUY"
    assert call["quantity"] == 1
