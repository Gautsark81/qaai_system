# Path: tests/test_dhan_safe_client_integration.py
"""Integration-like tests for DhanSafeClient using a mocked requester function."""
import pytest
from src.clients.dhan_safe_client import DhanSafeClient, SafeResponse, NetworkError, CircuitOpenError

class MockResp:
    def __init__(self, status, json_body=None, headers=None, text=""):
        self.status_code = status
        self._json = json_body
        self.headers = headers or {}
        self.text = text

    def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json

def test_place_order_success():
    calls = []
    def requester(method, url, headers=None, json=None, timeout=10):
        calls.append((method, url, json))
        return MockResp(201, {"order_id": "abc123"})

    client = DhanSafeClient(api_key="k", requester=requester)
    r = client.safe_place_order({"symbol": "INFY", "qty": 1})
    assert r.success
    assert r.data["order_id"] == "abc123"

def test_rate_limit_then_success():
    sequence = [
        MockResp(429, {"error": "rate limit"}, headers={"Retry-After": "0"}),
        MockResp(201, {"order_id": "ok"}),
    ]
    idx = {"i": 0}
    def requester(method, url, headers=None, json=None, timeout=10):
        resp = sequence[idx["i"]]
        idx["i"] += 1
        return resp

    client = DhanSafeClient(api_key="k", requester=requester, max_retries=3)
    r = client.safe_place_order({"symbol": "TCS", "qty": 1})
    assert r.success and r.data["order_id"] == "ok"

def test_circuit_opens_after_failures():
    def requester(method, url, headers=None, json=None, timeout=10):
        return MockResp(500, {"error": "server"})

    client = DhanSafeClient(api_key="k", requester=requester, max_retries=1, circuit_fail_threshold=2)
    with pytest.raises(Exception):
        client._request("GET", "/v1/positions")
    # second failure should open circuit
    with pytest.raises(Exception):
        client._request("GET", "/v1/positions")
    # Now the circuit should be open and reject immediately
    with pytest.raises(CircuitOpenError):
        client._request("GET", "/v1/positions")
