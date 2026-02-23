# tests/test_dhan_safe_client_mock.py
import pytest
from clients.dhan_safe_client import MockDhanSafeClient

def test_mock_place_cancel_status():
    c = MockDhanSafeClient()
    o = c.place_order("TST", "BUY", qty=1, price=100.0)
    assert "order_id" in o
    oid = o["order_id"]

    status = c.get_order_status(oid)
    assert status["status"] == "NEW"
    assert status["price"] == 100.0 or float(status["price"]) == 100.0

    c.cancel_order(oid)
    cancelled = c.get_order_status(oid)
    assert cancelled["status"] == "CANCELLED"

    with pytest.raises(KeyError):
        c.get_order_status("nonexistent")
