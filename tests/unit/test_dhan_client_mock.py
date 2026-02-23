# tests/unit/test_dhan_client_mock.py
from clients.dhan_safe_client import DhanSafeClient

def test_dhan_safe_client_fills():
    c = DhanSafeClient(safe_mode=True)
    resp = c.send_order({"symbol":"TST","qty":1,"price":10,"side":"buy"})
    assert isinstance(resp, dict)
    assert "order_id" in resp
    assert resp["status"] == "filled"
    oid = resp["order_id"]
    got = c._get_order(oid)
    assert got is not None
    assert got["status"] == "filled"

def test_cancel_nonexistent():
    c = DhanSafeClient(safe_mode=True)
    res = c.cancel_order("no-such")
    assert res["status"] == "not_found"
