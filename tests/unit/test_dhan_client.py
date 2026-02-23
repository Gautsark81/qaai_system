# tests/unit/test_dhan_client.py
import json
import pytest
import requests
from types import SimpleNamespace
from unittest.mock import Mock

from infra.dhan_client import DhanClient, DhanAPIError

class DummyResp:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json

    def close(self):
        pass

class DummySession:
    def __init__(self, responses):
        # responses: list of DummyResp
        self._responses = list(responses)
        self.request_count = 0

    def get(self, url, params=None, headers=None, timeout=None):
        self.request_count += 1
        if not self._responses:
            raise requests.RequestException("no response")
        return self._responses.pop(0)

    def mount(self, *a, **k):
        pass

    def close(self):
        pass

def test_fetch_ohlcv_success_list(monkeypatch):
    client = DhanClient(base_url="https://api.mock", api_key="k", api_secret="s")
    # inject session that returns well-formed data
    data = {"data": [{"time": "2023-01-01T00:00:00Z", "open": 10, "high": 11, "low": 9, "close": 10.5, "volume": 100}]}
    session = DummySession([DummyResp(200, json_data=data)])
    client.set_session(session)
    res = client.fetch_ohlcv("NSE:XYZ", as_df=False)
    assert isinstance(res, list)
    assert res[0]["open"] == 10

@pytest.mark.skipif(True, reason="pandas optional in test env")
def test_fetch_ohlcv_as_df(monkeypatch):
    client = DhanClient(base_url="https://api.mock")
    data = {"data": [{"time": "2023-01-01T00:00:00Z", "open": 10, "high": 11, "low": 9, "close": 10.5, "volume": 100}]}
    session = DummySession([DummyResp(200, json_data=data)])
    client.set_session(session)
    df = client.fetch_ohlcv("NSE:XYZ", as_df=True)
    import pandas as pd
    assert hasattr(df, "iloc")

def test_fetch_ohlcv_bad_payload_raises():
    client = DhanClient(base_url="https://api.mock")
    session = DummySession([DummyResp(200, json_data={"bad": "payload"})])
    client.set_session(session)
    with pytest.raises(DhanAPIError):
        client.fetch_ohlcv("NSE:XYZ", as_df=False)

def test_network_error_raises():
    client = DhanClient(base_url="https://api.mock")
    # session that raises RequestException
    class BadSession:
        def get(self, *a, **k):
            raise requests.RequestException("boom")
        def mount(self, *a, **k):
            pass
        def close(self):
            pass
    client.set_session(BadSession())
    with pytest.raises(DhanAPIError):
        client.fetch_ohlcv("NSE:XYZ", as_df=False)

def test_get_top_nse_stocks_by_volume_success():
    client = DhanClient(base_url="https://api.mock")
    payload = {"data":[{"symbol":"NSE:ABC","volume":1000}]}
    session = DummySession([DummyResp(200, json_data=payload)])
    client.set_session(session)
    res = client.get_top_nse_stocks_by_volume(limit=1)
    assert isinstance(res, list)
    assert res[0]["symbol"] == "NSE:ABC"
