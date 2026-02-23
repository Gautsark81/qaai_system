# infra/dhan_client.py
"""
Hardened DhanClient

Features:
- requests.Session with Retry/backoff (urllib3 Retry) and module-level fallback
- CircuitBreaker: trips after consecutive failures and enforces cool-down
- TokenBucket rate limiter to control request rate
- Tolerant fetch_ohlcv payload normalization and both short/long keys
- set_session() for injected DummySession in tests
- Module-level requests.get calls when no session injected so tests can patch requests.get
"""
from __future__ import annotations

import logging
import time
import threading
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("infra.dhan_client")
logger.addHandler(logging.NullHandler())

try:
    import pandas as pd  # optional for as_df
except Exception:
    pd = None


class DhanAPIError(RuntimeError):
    """Raised for API-level problems."""


class CircuitBreaker:
    """Simple stateful circuit breaker."""

    def __init__(self, max_failures: int = 5, reset_timeout_sec: int = 300):
        self.max_failures = int(max_failures)
        self.reset_timeout_sec = int(reset_timeout_sec)
        self._failures = 0
        self._tripped_at: Optional[float] = None
        self._lock = threading.Lock()

    def record_success(self):
        with self._lock:
            self._failures = 0
            self._tripped_at = None

    def record_failure(self):
        with self._lock:
            self._failures += 1
            if self._failures >= self.max_failures:
                self._tripped_at = time.time()

    def is_tripped(self) -> bool:
        with self._lock:
            if self._tripped_at is None:
                return False
            if (time.time() - self._tripped_at) >= self.reset_timeout_sec:
                # auto-reset after timeout
                self._failures = 0
                self._tripped_at = None
                return False
            return True

    def time_until_reset(self) -> Optional[float]:
        with self._lock:
            if self._tripped_at is None:
                return None
            return max(0.0, self.reset_timeout_sec - (time.time() - self._tripped_at))


class TokenBucket:
    """
    Very small token-bucket rate limiter.
    capacity: max tokens stored
    refill_rate: tokens per second
    """

    def __init__(self, capacity: float = 5.0, refill_rate: float = 1.0):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self._tokens = float(capacity)
        self._last = time.time()
        self._lock = threading.Lock()

    def _refill(self):
        now = time.time()
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

    def wait_for_token(self, timeout: float = 5.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.consume(1.0):
                return True
            time.sleep(0.05)
        return False


class DhanClient:
    DEFAULT_TIMEOUT = 10
    DEFAULT_RETRIES = 3
    DEFAULT_BACKOFF_FACTOR = 0.3
    DEFAULT_STATUS_FORCELIST = (429, 500, 502, 503, 504)

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: str = "https://api.dhan.com",
        timeout: Optional[int] = None,
        retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        circuit_max_failures: int = 5,
        circuit_reset_sec: int = 300,
        rate_capacity: float = 10.0,
        rate_refill: float = 1.0,
    ):
        self.api_key = api_key or ""
        self.api_secret = api_secret or ""
        self.base_url = base_url.rstrip("/")
        self.timeout = int(timeout or self.DEFAULT_TIMEOUT)
        self.retries = int(retries if retries is not None else self.DEFAULT_RETRIES)
        self.backoff_factor = float(backoff_factor if backoff_factor is not None else self.DEFAULT_BACKOFF_FACTOR)

        self._session = self._build_session()
        self._injected_session = False

        # circuit breaker and rate limiter
        self.circuit = CircuitBreaker(max_failures=circuit_max_failures, reset_timeout_sec=circuit_reset_sec)
        self.rate_limiter = TokenBucket(capacity=rate_capacity, refill_rate=rate_refill)

    def _build_session(self) -> requests.Session:
        s = requests.Session()
        retry = Retry(
            total=self.retries,
            read=self.retries,
            connect=self.retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.DEFAULT_STATUS_FORCELIST,
            allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_maxsize=10, pool_connections=10)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        return s

    def set_session(self, session: requests.Session) -> None:
        """Inject a custom session (e.g., DummySession in tests)."""
        self._session = session
        self._injected_session = True

    def close(self) -> None:
        try:
            self._session.close()
        except Exception:
            pass

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        return headers

    def _preflight_check(self):
        """Fail fast if circuit is tripped."""
        if self.circuit.is_tripped():
            t = self.circuit.time_until_reset()
            raise DhanAPIError(f"Circuit breaker tripped (retry after {t:.1f}s)" if t is not None else "Circuit breaker tripped")

        # rate limiter: wait a short time for token; if cannot get, raise early
        ok = self.rate_limiter.wait_for_token(timeout=2.0)
        if not ok:
            raise DhanAPIError("Rate limiter: could not obtain token within timeout")

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Internal GET helper. Uses module-level requests.get when no injected session
        so tests that patch infra.dhan_client.requests.get will work.
        """
        self._preflight_check()
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            if getattr(self, "_injected_session", False):
                resp = self._session.get(url, params=params or {}, headers=self._headers(), timeout=self.timeout)
            else:
                resp = requests.get(url, params=params or {}, headers=self._headers(), timeout=self.timeout)
        except requests.RequestException as e:
            # register failure and raise
            self.circuit.record_failure()
            logger.debug("HTTP request failed: %s %s", url, repr(e))
            raise DhanAPIError(f"Network error while calling Dhan API: {e}") from e

        status = getattr(resp, "status_code", 0) or 0
        if status >= 400:
            # treat as failure
            self.circuit.record_failure()
            logger.warning("Dhan API returned HTTP %s for %s", status, url)
            raise DhanAPIError(f"Dhan API returned HTTP {status}")

        # try parse json
        try:
            data = resp.json()
        except Exception as e:
            self.circuit.record_failure()
            logger.warning("Dhan API returned non-JSON response for %s", url)
            raise DhanAPIError("Dhan API returned non-JSON response") from e

        if not isinstance(data, dict):
            self.circuit.record_failure()
            raise DhanAPIError("Dhan API returned unexpected payload type")

        # success -> reset failure counter
        self.circuit.record_success()
        return data

    def fetch_ohlcv(
        self, symbol: str, timeframe: str = "1d", limit: int = 200, as_df: bool = False
    ) -> List[Dict[str, Any]] | "pd.DataFrame":
        """
        Fetch OHLCV bars.

        Supports either:
          - fetch_ohlcv(symbol, timeframe='1d', limit=200)
          - fetch_ohlcv(symbol, start_date='YYYY-MM-DD', end_date='YYYY-MM-DD')
        """
        from datetime import datetime

        def _looks_like_date(s: Any) -> bool:
            if not isinstance(s, str):
                return False
            try:
                datetime.fromisoformat(s)
                return True
            except Exception:
                return False

        path = f"v1/ohlcv/{symbol}"
        params: Dict[str, Any] = {}

        if _looks_like_date(timeframe) and _looks_like_date(limit):
            params["start"] = timeframe
            params["end"] = limit
        else:
            params["timeframe"] = timeframe
            try:
                params["limit"] = int(limit)
            except Exception:
                pass

        payload = self._get(path, params=params)

        if "data" not in payload:
            raise DhanAPIError("Dhan API missing 'data' in OHLCV response")
        data = payload["data"]
        if not isinstance(data, list):
            raise DhanAPIError("Dhan OHLCV 'data' is not a list")

        normalized: List[Dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            time_val = item.get("t") or item.get("time") or item.get("timestamp") or item.get("ts") or None
            open_val = item.get("o") or item.get("open")
            high_val = item.get("h") or item.get("high")
            low_val = item.get("l") or item.get("low")
            close_val = item.get("c") or item.get("close")
            vol_val = item.get("v") or item.get("volume")
            bar = {
                "t": time_val, "o": open_val, "h": high_val, "l": low_val, "c": close_val, "v": vol_val,
                "time": time_val, "open": open_val, "high": high_val, "low": low_val, "close": close_val, "volume": vol_val,
            }
            normalized.append(bar)

        if as_df:
            if pd is None:
                raise RuntimeError("pandas is required for as_df=True")
            df = pd.DataFrame(normalized)
            try:
                df["time"] = pd.to_datetime(df["time"])
            except Exception:
                pass
            return df
        return normalized

    def get_top_nse_stocks_by_volume(self, limit: int = 50) -> List[Dict[str, Any]]:
        path = "v1/market/top-volume"
        params = {"exchange": "NSE", "limit": int(limit)}
        payload = self._get(path, params=params)
        if "data" not in payload or not isinstance(payload["data"], list):
            raise DhanAPIError("Dhan API missing/invalid 'data' in top-volume response")
        return payload["data"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.close()
        except Exception:
            pass
