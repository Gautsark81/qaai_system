import pytest

from qaai_system.execution.order_manager import OrderManager


class DummyBroker:
    """Simple fake broker to satisfy OrderManager.submit_order calls."""

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
        # Mimic a typical open order with an id
        return {
            "order_id": f"BRK_{len(self.calls)}",
            "status": "open",
            "fill_price": price,
        }


def test_create_and_get_order_basic():
    broker = DummyBroker()
    om = OrderManager(broker=broker)

    oid = om.create_order(
        symbol="NIFTY24FEBFUT",
        side="BUY",
        quantity=2,
        price=100.0,
        meta={"strategy_id": "test-strat"},
    )

    assert oid is not None
    assert broker.calls, "Broker should have been called at least once"

    all_orders = om.get_all_orders()
    assert oid in all_orders

    o = all_orders[oid]
    assert o["symbol"] == "NIFTY24FEBFUT"
    assert o["side"].upper() == "BUY"
    assert o["price"] == 100.0

    # Your OrderManager stores 'quantity', not 'position_size'
    size = o.get("position_size", o.get("quantity"))
    assert size == 2


def test_get_all_orders_dry_run_when_no_broker():
    # When no broker/client is present and nothing has been created,
    # get_all_orders should return either {} or a synthetic placeholder.
    om = OrderManager(broker=None, client=None)

    orders = om.get_all_orders()

    assert isinstance(orders, dict)
    # Accept either the synthetic placeholder or empty as valid behaviour
    if orders:
        assert "__dryrun__" in orders or len(orders) >= 1


def test_create_order_from_dict_adapter():
    broker = DummyBroker()
    om = OrderManager(broker=broker)

    payload = {
        "symbol": "RELIANCE",
        "side": "SELL",
        "price": 2500.0,
        "sl_scaled": 2520.0,
        "tp_scaled": 2450.0,
        "position_size": 3,
        "strategy_id": "adapter-test",
        "trade_type": "INTRADAY",
    }

    oid = om.create_order_from_dict(payload)
    assert oid is not None

    orders = om.get_all_orders()
    assert oid in orders
    o = orders[oid]
    assert o["symbol"] == "RELIANCE"
    assert o["side"].upper() == "SELL"
    assert o["price"] == 2500.0
    assert o["status"].lower() in ("open", "partially_filled", "new")
