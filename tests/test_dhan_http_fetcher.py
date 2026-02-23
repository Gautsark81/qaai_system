# tests/test_dhan_http_fetcher.py
import pytest
from modules.data_pipeline.providers.dhan_http_fetcher import DhanHTTPFetcher, HTTPFetchError
import requests
from unittest.mock import patch, Mock
import pandas as pd

def make_response(status=200, json_data=None, headers=None):
    r = Mock()
    r.status_code = status
    r.ok = status >= 200 and status < 300
    r.json = Mock(return_value=json_data or {})
    r.text = str(json_data)[:200]
    r.headers = headers or {}
    return r

@patch("modules.data_pipeline.providers.dhan_http_fetcher.requests.Session.request")
def test_fetch_ohlcv_list_shape(mock_req):
    sample = {"data": [
        {"timestamp": "2025-01-01T00:00:00Z", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 1234},
        {"timestamp": "2025-01-02T00:00:00Z", "open": 100.5, "high": 102, "low": 100, "close": 101.0, "volume": 4321},
    ]}
    mock_req.return_value = make_response(200, sample)
    f = DhanHTTPFetcher(base_url="https://api.example", api_key=None, max_retries=1)
    df = f.fetch_ohlcv("X", "2025-01-01", "2025-01-02")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 2

@patch("modules.data_pipeline.providers.dhan_http_fetcher.requests.Session.request")
def test_fetch_ohlcv_unsupported_shape_raises(mock_req):
    mock_req.return_value = make_response(200, {"foo": "bar"})
    f = DhanHTTPFetcher(base_url="https://api.example", api_key=None, max_retries=1, backoff_factor=0.01)
    with pytest.raises(HTTPFetchError):
        f.fetch_ohlcv("X", "2025-01-01", "2025-01-02")

@patch("modules.data_pipeline.providers.dhan_http_fetcher.requests.Session.request")
def test_retry_on_500_then_success(mock_req):
    # first attempt 500, second 200
    mock_req.side_effect = [
        make_response(500, {"error":"oops"}),
        make_response(200, {"data": [{"timestamp": "2025-01-01T00:00:00Z", "open": 1, "high":1, "low":1, "close":1, "volume":1}]}),
    ]
    f = DhanHTTPFetcher(base_url="https://api.example", api_key=None, max_retries=3, backoff_factor=0.001)
    df = f.fetch_ohlcv("X", "2025-01-01", "2025-01-02")
    assert len(df) == 1
