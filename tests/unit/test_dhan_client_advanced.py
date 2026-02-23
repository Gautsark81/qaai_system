# tests/unit/test_dhan_client_advanced.py
import pytest
import time
import requests
from infra.dhan_client import DhanClient, DhanAPIError, TokenBucket, CircuitBreaker

class DummyResp:
    def __init__(self, status=200, json_data=None):
        self.status_code = status
        self._json = json_data or {"data": []}
    def json(self):
        return self._json

class DummySession:
    def __init__(self, responses):
        # responses: iterable of DummyResp
        self._iter = iter(responses)
    def get(self, *a, **k):
        try:
            return next(self._iter)
        except StopIteration:
            return DummyResp(200, {"data": []})
    def close(self):
        pass
    def mount(self, *a, **k):
        pass

def test_token_bucket_consumes_and_refills():
    tb = TokenBucket(capacity=2, refill_rate=1.0)
    assert tb.consume(1.0)
    assert tb.consume(1.0)
    assert not tb.consume(1.0)
    # wait a bit for refill
    time.sleep(1.2)
    assert tb.consume(1.0)

def test_circuit_breaker_trips_and_resets():
    cb = CircuitBreaker(max_failures=2, reset_timeout_sec=1)
    assert not cb.is_tripped()
    cb.record_failure()
    assert not cb.is_tripped()
    cb.record_failure()
    assert cb.is_tripped()
    # wait for reset
    time.sleep(1.1)
    assert not cb.is_tripped()
    cb.record_failure()
    assert not cb.is_tripped()

def test_fetch_ohlcv_with_injected_session():
    data = {"data":[{"t":"2025-01-01","o":1,"h":2,"l":0,"c":1.5,"v":100}]}
    session = DummySession([DummyResp(200, json_data=data)])
    client = DhanClient()
    client.set_session(session)
    res = client.fetch_ohlcv("NSE:XYZ", as_df=False)
    assert isinstance(res, list)
    assert res[0]["o"] == 1

def test_circuit_breaker_blocks_on_failures():
    # session that returns HTTP 500 twice
    session = DummySession([DummyResp(500, {}), DummyResp(500, {})])
    client = DhanClient(circuit_max_failures=2, circuit_reset_sec=2)
    client.set_session(session)
    with pytest.raises(DhanAPIError):
        client.fetch_ohlcv("NSE:XYZ", as_df=False)
    # second call should also raise but now circuit is tripped
    with pytest.raises(DhanAPIError):
        client.fetch_ohlcv("NSE:XYZ", as_df=False)

def test_rate_limiter_blocks_when_exhausted(monkeypatch):
    client = DhanClient(rate_capacity=1, rate_refill=0.0)  # no refill
    # patch _preflight_check to use rate_limiter.wait_for_token default behavior (already used)
    # inject a dummy session that would otherwise succeed
    session = DummySession([DummyResp(200, {"data": []})])
    client.set_session(session)
    # first call consumes token
    _ = client.fetch_ohlcv("NSE:XYZ", as_df=False)
    # immediate second should raise due to rate limiter
    with pytest.raises(DhanAPIError):
        client.fetch_ohlcv("NSE:XYZ", as_df=False)
