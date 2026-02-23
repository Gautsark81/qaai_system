# tests/test_order_manager.py
import time
import pytest
from clients.dhan_safe_client import MockDhanSafeClient
from clients.order_manager import OrderManager

class FailOnceClient(MockDhanSafeClient):
    """
    A client that fails first `n_failures` calls to place_order, then succeeds.
    Used to test retry logic.
    """
    def __init__(self, n_failures=1):
        super().__init__()
        self._failures = n_failures
        self._calls = 0

    def place_order(self, *args, **kwargs):
        self._calls += 1
        if self._calls <= self._failures:
            raise RuntimeError("transient error")
        return super().place_order(*args, **kwargs)


def test_place_order_success_and_cache():
    client = MockDhanSafeClient()
    om = OrderManager(client)
    meta = om.place_order("TST", "BUY", qty=1, price=100.0, idempotency_key="abc123")
    assert "order_id" in meta
    assert meta["symbol"] == "TST"
    # idempotency lookup returns same order
    meta2 = om.place_order("TST", "BUY", qty=1, price=100.0, idempotency_key="abc123")
    assert meta2["order_id"] == meta["order_id"]
    # local listing includes order
    local = om.list_local_orders()
    assert meta["order_id"] in local

def test_retry_on_transient_error():
    client = FailOnceClient(n_failures=1)
    # allow 3 retries to be safe
    om = OrderManager(client, max_retries=3, backoff_base=0.01)
    meta = om.place_order("TST", "BUY", qty=1, price=50.0, idempotency_key="k1")
    assert "order_id" in meta
    # ensure we eventually have the order cached
    assert om.lookup_by_idempotency_key("k1") is not None

def test_cancel_and_status_update():
    client = MockDhanSafeClient()
    om = OrderManager(client)
    meta = om.place_order("T", "SELL", qty=2, price=10.0, idempotency_key="k2")
    oid = meta["order_id"]
    # cancel
    cmeta = om.cancel_order(oid)
    assert cmeta["status"] == "CANCELLED"
    # get status should reflect cancelled
    status = om.get_order_status(oid)
    assert status["status"] == "CANCELLED"

def test_get_status_fallback_to_local_when_client_raises(monkeypatch):
    client = MockDhanSafeClient()
    om = OrderManager(client)
    meta = om.place_order("X", "BUY", qty=1, price=1.0, idempotency_key="i1")
    oid = meta["order_id"]

    # monkeypatch client.get_order_status to raise
    def fail_status(order_id):
        raise RuntimeError("remote down")
    monkeypatch.setattr(client, "get_order_status", fail_status)

    # should return local cached metadata (no raise)
    status = om.get_order_status(oid)
    assert status["order_id"] == oid
