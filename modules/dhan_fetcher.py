# modules/dhan_fetcher.py
import time
import threading
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter (thread-safe).
    capacity: max tokens
    refill_rate: tokens per second
    """
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self._tokens = float(capacity)
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last
        if elapsed <= 0:
            return
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
        self._last = now

    def consume(self, tokens: float = 1.0) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def wait(self, tokens: float = 1.0):
        """Block until tokens are available, then consume."""
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                # compute wait time until one token is available
                missing = tokens - self._tokens
                wait_seconds = max( (missing / self.refill_rate), 0.01 )
            time.sleep(wait_seconds)


def build_requests_session(total_retries: int = 5, backoff_factor: float = 0.5,
                           status_forcelist=(429, 500, 502, 503, 504)) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=total_retries,
        read=total_retries,
        connect=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']),
        raise_on_status=False,  # we'll handle status codes manually (so 429 isn't raised)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class DhanFetcherSync:
    """
    Example Dhan fetcher with retry/backoff and rate-limiting guard.
    - rate_limiter: TokenBucketRateLimiter(capacity, refill_rate)
    - session: requests.Session with urllib3.Retry mounted
    """
    def __init__(self,
                 api_key: str,
                 base_url: str = "https://api.dhan.com",
                 rate_limiter: Optional[TokenBucketRateLimiter] = None,
                 session: Optional[requests.Session] = None):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.rate_limiter = rate_limiter or TokenBucketRateLimiter(capacity=10, refill_rate=2)  # default: 2 req/s burst 10
        self.session = session or build_requests_session()

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "qaai_system/dhan_fetcher/1.0"
        }

    def request(self, method: str, path: str, params=None, json=None, headers: Dict[str, str] = None, timeout: float = 10.0) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        # Wait for tokens (rate limit guard)
        self.rate_limiter.wait(tokens=1.0)

        hdrs = self._build_headers()
        if headers:
            hdrs.update(headers)

        # Outer retry wrapper to handle special 429 Retry-After behavior
        max_attempts = 6
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                resp = self.session.request(method=method, url=url, params=params, json=json, headers=hdrs, timeout=timeout)
            except requests.RequestException as e:
                # network-level error: apply exponential backoff and retry
                wait = min(60, (2 ** attempt) * 0.5)
                time.sleep(wait)
                continue

            if resp.status_code == 429:
                # respect Retry-After if present, else exponential backoff
                ra = resp.headers.get("Retry-After")
                if ra:
                    try:
                        wait = float(ra)
                    except ValueError:
                        # could be a HTTP-date; fall back to a default
                        wait = 5.0
                else:
                    wait = min(60, (2 ** attempt) * 0.5)
                # optionally log here
                time.sleep(wait)
                continue

            # other 5xx: let urllib3's Retry handle many cases, but if we get here inspect and backoff
            if 500 <= resp.status_code < 600:
                wait = min(60, (2 ** attempt) * 0.5)
                time.sleep(wait)
                continue

            # success-ish: 2xx or 4xx non-retryable
            try:
                return {"status_code": resp.status_code, "json": resp.json(), "text": resp.text, "headers": resp.headers}
            except ValueError:
                return {"status_code": resp.status_code, "json": None, "text": resp.text, "headers": resp.headers}

        raise RuntimeError(f"Max attempts exceeded for {method} {url}")


# Example usage:
if __name__ == "__main__":
    fetcher = DhanFetcherSync(api_key="MYKEY", base_url="https://sandbox.dhan.co")
    res = fetcher.request("GET", "/market/ticker", params={"symbol": "RELIANCE"})
    print(res["status_code"], res["json"])
