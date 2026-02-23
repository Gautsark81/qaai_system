# tests/test_broker_signature_adapter.py
import pytest
from qaai_system.execution.order_manager import OrderManager


class KwargsBroker:
    def __init__(self):
        self.calls = []

    def submit_order(self, **kwargs):
        self.calls.append(("kwargs", kwargs))
        # return a minimal dict expected by order manager
        return {"order_id": "brk_kw_1", "status": "open"}


class DictBroker:
    def __init__(self):
        self.calls = []

    def submit_order(self, payload):
        self.calls.append(("dict", payload))
        return {"order_id": "brk_dict_1", "status": "open"}


class PositionalBroker:
    def __init__(self):
        self.calls = []

    # Accepts symbol, side, quantity, price, order_meta=None
    def submit_order(self, symbol, side, quantity, price, order_meta=None):
        self.calls.append(("pos", (symbol, side, quantity, price, order_meta)))
        return {"order_id": "brk_pos_1", "status": "open"}


def test_broker_accepts_kwargs():
    b = KwargsBroker()
    om = OrderManager(broker=b, config={"approved_for_live": True}, mode="live")
    oid = om.create_order("ABC", "BUY", 1, 10.0, {"strategy_id": "t1"})
    assert oid is not None
    assert b.calls, "kwargs broker not called"


def test_broker_accepts_single_dict():
    b = DictBroker()
    om = OrderManager(broker=b, config={"approved_for_live": True}, mode="live")
    oid = om.create_order("XYZ", "SELL", 2, 5.0, {"strategy_id": "t2"})
    assert oid is not None
    assert b.calls, "dict broker not called"


def test_broker_accepts_positional():
    b = PositionalBroker()
    om = OrderManager(broker=b, config={"approved_for_live": True}, mode="live")
    oid = om.create_order("MOCK", "BUY", 3, 1.0, {"strategy_id": "t3"})
    assert oid is not None
    assert b.calls, "positional broker not called"
