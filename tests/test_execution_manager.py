# tests/test_execution_manager.py
import pytest
from modules.order.manager import (
    SQLiteStore,
    OrderManager,
    Router,
    ExecutionEngineHTTP
)
from types import SimpleNamespace

# ------------------
# Dummy Engine
# ------------------
class DummyEngine:
    def __init__(self, accept=True):
        self.accept = accept
        self.sent = []
        self.cancelled = []
        self.tag = "DUMMY"

    def send_order(self, coid, payload, timeout=10):
        self.sent.append((coid, payload))
        if self.accept:
            return {"status": "ok", "broker_order_id": f"BRK-{coid}"}
        raise RuntimeError("dummy rejection")

    def cancel_order(self, coid, broker_order_id=None, timeout=10):
        self.cancelled.append(coid)
        return {"status": "ok"}


# ------------------
# Tests
# ------------------

def test_create_and_send_success():
    store = SQLiteStore(":memory:")
    eng = DummyEngine(accept=True)
    router = Router([("D1", eng)])

    om = OrderManager(store, router)

    rec = om.create_and_send("INFY", "BUY", qty=10, price=1500.0)
    assert rec["state"] in ("ACKED", "SENT")
    assert store.get_order(rec["client_order_id"]) is not None


def test_idempotent_client_hint():
    store = SQLiteStore(":memory:")
    eng = DummyEngine(accept=True)
    router = Router([("D1", eng)])

    om = OrderManager(store, router)

    o1 = om.create_and_send("INFY", "BUY", 10, price=1000.0, client_id_hint="ABC")
    o2 = om.create_and_send("INFY", "BUY", 10, price=1000.0, client_id_hint="ABC")

    assert o1["client_order_id"] == o2["client_order_id"]


def test_handle_partial_fill():
    store = SQLiteStore(":memory:")
    eng = DummyEngine(accept=True)
    router = Router([("D1", eng)])
    om = OrderManager(store, router)

    rec = om.create_and_send("TCS", "BUY", 10, price=3000.0)
    coid = rec["client_order_id"]

    # fill 3 shares
    om.handle_fill_event(coid, filled_qty=3, fill_price=3002.0)
    updated = store.get_order(coid)

    assert updated["filled_qty"] == 3
    assert updated["state"] == "PART_FILLED"


def test_full_fill_completion():
    store = SQLiteStore(":memory:")
    eng = DummyEngine(accept=True)
    router = Router([("D1", eng)])
    om = OrderManager(store, router)

    rec = om.create_and_send("TCS", "BUY", 10, price=3000.0)
    coid = rec["client_order_id"]

    # fill all 10
    om.handle_fill_event(coid, filled_qty=10, fill_price=3000.0)
    updated = store.get_order(coid)

    assert updated["state"] == "FILLED"
    assert updated["filled_qty"] == 10


def test_cancel_order():
    store = SQLiteStore(":memory:")
    eng = DummyEngine(accept=True)
    router = Router([("D1", eng)])
    om = OrderManager(store, router)

    rec = om.create_and_send("BANKNIFTY", "SELL", 2, price=48000)
    coid = rec["client_order_id"]

    out = om.cancel_order(coid)
    assert out["state"] == "CANCELED"


def test_reconcile():
    store = SQLiteStore(":memory:")
    eng = DummyEngine(accept=True)
    router = Router([("D1", eng)])
    om = OrderManager(store, router)

    rec = om.create_and_send("ITC", "BUY", 1, price=450)
    # Just ensure it doesn't raise
    om.reconcile()
