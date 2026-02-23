# tests/test_dhan_http_provider.py
import json
from providers.dhan_http import DhanHTTPProvider


def test_dhan_http_simulated_mode():
    dp = DhanHTTPProvider(config={"starting_cash": 1000, "enable_http": False})
    dp.connect()
    assert dp.is_connected()
    resp = dp.submit_order({"symbol": "TST", "side": "buy", "quantity": 2, "price": 10})
    assert resp.get("status") == "filled"
    assert dp.get_positions().get("TST") == 2
    assert dp.get_account_nav() == 1000 - 2 * 10


def test_dhan_http_http_mode_monkeypatch(monkeypatch):
    # simulate requests.post returning JSON
    class FakeResp:
        def __init__(self, code, data):
            self.status_code = code
            self._data = data
            self.text = json.dumps(data)

        def json(self):
            return self._data

    def fake_post(url, json=None, headers=None, timeout=None):
        return FakeResp(
            201,
            {
                "status": "filled",
                "order_id": "oh1",
                "filled_qty": int(json.get("quantity") or 0),
                "price": json.get("price"),
            },
        )

    # create provider with HTTP enabled
    dp = DhanHTTPProvider(
        config={
            "starting_cash": 1000,
            "enable_http": True,
            "api_base": "https://api.test",
        }
    )
    # monkeypatch requests module inside provider
    monkeypatch.setattr(
        "providers.dhan_http.requests", None, raising=False
    )  # ensure attribute exists
    # now actually insert our fake requests module as attribute
    dp._requests = type("R", (), {"post": staticmethod(fake_post)})
    dp._enable_http = True
    dp._connected = True
    resp = dp.submit_order({"symbol": "TST", "side": "buy", "quantity": 3, "price": 5})
    assert resp.get("status") == "filled"
    assert resp.get("filled_qty") == 3
