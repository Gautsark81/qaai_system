# tests/test_dhan_fetcher_rate_limit.py
import time
from modules.dhan_fetcher import TokenBucketRateLimiter, DhanFetcherSync

def test_token_bucket_consumption():
    tb = TokenBucketRateLimiter(capacity=2, refill_rate=1)  # 1 token/sec
    assert tb.consume(1.0) is True
    assert tb.consume(1.0) is True
    assert tb.consume(1.0) is False
    time.sleep(1.1)
    assert tb.consume(1.0) is True

def test_request_respects_rate_limiter(monkeypatch):
    # monkeypatch the session.request to count calls without actually doing network IO
    class DummyResponse:
        def __init__(self, status=200, json_data=None):
            self.status_code = status
            self._json = json_data or {"ok": True}
            self.headers = {}
            self.text = '{"ok": true}'
        def json(self):
            return self._json

    calls = []
    def fake_request(method, url, params=None, json=None, headers=None, timeout=None):
        calls.append((method, url))
        return DummyResponse(status=200)

    fetcher = DhanFetcherSync(api_key="x", base_url="https://api.test")
    monkeypatch.setattr(fetcher.session, "request", fake_request)

    # make 3 calls quickly - default limiter allows 2 tokens then blocks until refill
    fetcher.rate_limiter = TokenBucketRateLimiter(capacity=2, refill_rate=1)
    start = time.time()
    fetcher.request("GET", "/1")
    fetcher.request("GET", "/2")
    fetcher.request("GET", "/3")  # should wait ~1s for refill
    elapsed = time.time() - start
    assert len(calls) == 3
    assert elapsed >= 1.0 - 0.1
