# tests/test_dhan_fetcher.py
import json
import time
from unittest.mock import Mock, patch
import pandas as pd
from modules.data_pipeline.dhan_fetcher import DhanFetcher, DhanFetcherError, RateLimiter

def make_ohlcv_payload(n=3, base_ts=1609459200, base_price=100.0):
    rows = []
    for i in range(n):
        rows.append({
            "timestamp": base_ts + i*60,
            "open": base_price + i*0.1,
            "high": base_price + i*0.2 + 0.3,
            "low": base_price - 0.1 + i*0.05,
            "close": base_price + i*0.15,
            "volume": 1000 + i*10
        })
    return {"data": rows}

def make_ticks_payload(n=3, base_ts=1609459200, base_price=100.0):
    rows = []
    for i in range(n):
        rows.append({
            "timestamp": base_ts + i,
            "price": base_price + i*0.01,
            "size": 1 + i
        })
    return {"data": rows}

def test_fetch_ohlcv_parses_and_returns_dataframe():
    fake_json = make_ohlcv_payload()
    mock_sess = Mock()
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_json
    mock_sess.request.return_value = mock_resp

    fetcher = DhanFetcher(base_url="https://fake", session=mock_sess, rate_limiter=RateLimiter(min_interval_seconds=0))
    df = fetcher.fetch_ohlcv("ABC", start_ts=1609459200, end_ts=1609462800, interval="1m")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 3
    assert df.iloc[0].name is not None  # datetime index

def test_fetch_ticks_parses_and_returns_dataframe():
    fake_json = make_ticks_payload()
    mock_sess = Mock()
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_json
    mock_sess.request.return_value = mock_resp

    fetcher = DhanFetcher(base_url="https://fake", session=mock_sess, rate_limiter=RateLimiter(min_interval_seconds=0))
    df = fetcher.fetch_ticks("ABC", start_ts=1609459200, end_ts=1609459205)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["timestamp", "price", "size"]
    assert len(df) == 3

def test_retry_on_5xx_and_succeeds_eventually():
    # Simulate: first call returns 500, second returns 200
    mock_sess = Mock()
    resp_500 = Mock(status_code=500, text="server error")
    resp_200 = Mock(status_code=200, json=Mock(return_value=make_ohlcv_payload()))
    mock_sess.request.side_effect = [resp_500, resp_200]

    fetcher = DhanFetcher(base_url="https://fake", session=mock_sess, rate_limiter=RateLimiter(min_interval_seconds=0))
    df = fetcher.fetch_ohlcv("ABC", start_ts=1609459200, end_ts=1609462800)
    assert len(df) == 3
    # ensure we attempted at least twice
    assert mock_sess.request.call_count >= 2

def test_raises_on_malformed_payload():
    bad_payload = {"wrong": []}
    mock_sess = Mock()
    resp = Mock(status_code=200, json=Mock(return_value=bad_payload))
    mock_sess.request.return_value = resp
    fetcher = DhanFetcher(base_url="https://fake", session=mock_sess, rate_limiter=RateLimiter(min_interval_seconds=0))
    try:
        df = fetcher.fetch_ohlcv("ABC", start_ts=1, end_ts=2)
        # Should raise; if not, fail
        assert False, "Expected exception"
    except DhanFetcherError:
        pass
