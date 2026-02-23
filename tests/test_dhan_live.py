from unittest.mock import MagicMock, patch
from qaai_system.infra.dhan_live import DhanAdapterLive


def test_ping_success():
    a = DhanAdapterLive(client_id="x", access_token="y", base_url="https://mock")
    fake = MagicMock()
    fake.status_code = 200
    fake.json.return_value = {"holdings": []}
    with patch.object(a._session, "get", return_value=fake):
        ok, info = a.ping_broker()
        assert ok is True


def test_submit_order_map():
    a = DhanAdapterLive(client_id="x", access_token="y", base_url="https://mock")
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "order_id": "oid123",
        "status": "open",
        "avg_price": 100.0,
    }
    with patch.object(a._session, "post", return_value=resp):
        out = a.submit_order("RELIANCE", "buy", 1, 100.0)
        assert out["order_id"] == "oid123"
        assert out["status"].upper() == "OPEN"
