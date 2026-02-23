# modules/data_pipeline/dhan_fetcher.py
"""
DhanFetcher - minimal REST client with retry/backoff and simple rate limiting.

Features:
- fetch_ohlcv(symbol, start_ts, end_ts, interval) -> pandas.DataFrame with columns
  ['timestamp','open','high','low','close','volume'] and index as pd.DatetimeIndex
- fetch_ticks(symbol, start_ts, end_ts) -> pandas.DataFrame with columns
  ['timestamp','price','size']
- built-in retry with exponential backoff (with jitter)
- per-endpoint minimum interval rate limiter (simple cooldown)
- pluggable requests.Session for easier testing

Notes:
- This is intended as a robust local implementation for tests and small-scale usage.
- Replace base_url and auth handling to match your DhanHQ credentials / API.
"""

from __future__ import annotations
import time
import random
import logging
from typing import Optional, Dict, Any, List
import requests
import pandas as pd

logger = logging.getLogger(__name__)


class DhanFetcherError(Exception):
    pass


class RateLimiter:
    """Very small per-key cooldown limiter (not token-bucket)."""
    def __init__(self, min_interval_seconds: float = 0.2):
        self.min_interval_seconds = float(min_interval_seconds)
        self._last_call: Dict[str, float] = {}

    def wait(self, key: str):
        now = time.monotonic()
        last = self._last_call.get(key, 0.0)
        elapsed = now - last
        if elapsed < self.min_interval_seconds:
            to_wait = self.min_interval_seconds - elapsed
            time.sleep(to_wait)
        self._last_call[key] = time.monotonic()


def _retry_request(session: requests.Session, method: str, url: str, *,
                   params: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, Any]] = None,
                   json: Optional[Any] = None,
                   max_attempts: int = 4,
                   backoff_base: float = 0.5) -> requests.Response:
    """
    Wraps a requests call with simple exponential backoff and jitter.
    Retries on 5xx or network errors.
    """
    attempts = 0
    while True:
        attempts += 1
        try:
            resp = session.request(method, url, params=params, headers=headers, json=json, timeout=10)
            if 200 <= resp.status_code < 300:
                return resp
            # Retry on server errors (5xx)
            if 500 <= resp.status_code < 600:
                raise requests.HTTPError(f"Server error: {resp.status_code}", response=resp)
            # For 4xx, do not retry (client error)
            return resp
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
            if attempts >= max_attempts:
                logger.exception("Request failed after %d attempts: %s %s", attempts, method, url)
                raise DhanFetcherError(f"Request failed: {e}") from e
            # exponential backoff with small jitter
            sleep_for = backoff_base * (2 ** (attempts - 1)) * (0.8 + random.random() * 0.4)
            time.sleep(sleep_for)


class DhanFetcher:
    def __init__(self, base_url: str = "https://api.dhan.com", session: Optional[requests.Session] = None,
                 rate_limiter: Optional[RateLimiter] = None, api_key: Optional[str] = None):
        """
        base_url: API base URL (change to real Dhan HQ endpoint).
        session: requests.Session or None (a new session will be created).
        rate_limiter: RateLimiter instance for per-endpoint cooldowns.
        api_key: optional API key (insert into headers if provided).
        """
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.rate_limiter = rate_limiter or RateLimiter(min_interval_seconds=0.2)
        self.api_key = api_key

    def _headers(self) -> Dict[str, str]:
        h = {"Accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None, endpoint_key: Optional[str] = None) -> Dict[str, Any]:
        endpoint_key = endpoint_key or path
        self.rate_limiter.wait(endpoint_key)
        url = f"{self.base_url}{path}"
        resp = _retry_request(self.session, "GET", url, params=params, headers=self._headers())
        # If we received non-2xx and no exception (like 4xx), raise to caller
        if not (200 <= resp.status_code < 300):
            raise DhanFetcherError(f"HTTP {resp.status_code}: {resp.text}")
        return resp.json()

    def fetch_ohlcv(self, symbol: str, start_ts: int, end_ts: int, interval: str = "1m") -> pd.DataFrame:
        """
        Fetches OHLCV for a symbol between start_ts and end_ts (epoch seconds).
        Returns DataFrame with index=pd.DatetimeIndex and columns: open, high, low, close, volume.
        NOTE: The exact request/response schema will differ for the real API — update parsing accordingly.
        """
        # Example path and params — change to real Dhan API contract
        path = f"/v1/market/ohlcv/{symbol}"
        params = {"from": int(start_ts), "to": int(end_ts), "interval": interval}
        payload = self._get(path, params=params, endpoint_key="ohlcv")
        # Expect payload to contain list under 'data' or be a list itself
        rows = payload.get("data") if isinstance(payload, dict) else payload
        if rows is None:
            raise DhanFetcherError("Malformed OHLCV response: missing 'data' field")

        # Normalize rows into DataFrame - try common keys, be forgiving
        records = []
        for r in rows:
            # Accept keys: timestamp, t, time; price keys: o,h,l,c; volume: v
            ts = r.get("timestamp") or r.get("t") or r.get("time")
            open_p = r.get("open") or r.get("o")
            high_p = r.get("high") or r.get("h")
            low_p = r.get("low") or r.get("l")
            close_p = r.get("close") or r.get("c")
            vol = r.get("volume") or r.get("v") or 0
            if ts is None:
                continue
            records.append({
                "timestamp": int(ts),
                "open": float(open_p) if open_p is not None else None,
                "high": float(high_p) if high_p is not None else None,
                "low": float(low_p) if low_p is not None else None,
                "close": float(close_p) if close_p is not None else None,
                "volume": float(vol) if vol is not None else 0.0
            })

        if not records:
            # return empty frame with expected columns
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        df = pd.DataFrame(records)
        df["dt"] = pd.to_datetime(df["timestamp"], unit="s", utc=False)
        df = df.set_index("dt").sort_index()
        df = df[["open", "high", "low", "close", "volume"]].astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
        return df

    def fetch_ticks(self, symbol: str, start_ts: int, end_ts: int) -> pd.DataFrame:
        """
        Fetch tick data for the symbol in range. Returns DataFrame with columns: timestamp, price, size
        """
        path = f"/v1/market/ticks/{symbol}"
        params = {"from": int(start_ts), "to": int(end_ts)}
        payload = self._get(path, params=params, endpoint_key="ticks")
        rows = payload.get("data") if isinstance(payload, dict) else payload
        if rows is None:
            raise DhanFetcherError("Malformed ticks response: missing 'data' field")

        records = []
        for r in rows:
            ts = r.get("timestamp") or r.get("t") or r.get("time")
            price = r.get("price") or r.get("p")
            size = r.get("size") or r.get("s") or 0
            if ts is None or price is None:
                continue
            records.append({"timestamp": int(ts), "price": float(price), "size": float(size)})

        if not records:
            return pd.DataFrame(columns=["timestamp", "price", "size"])

        df = pd.DataFrame(records)
        df["dt"] = pd.to_datetime(df["timestamp"], unit="s", utc=False)
        df = df.set_index("dt").sort_index()
        df = df[["timestamp", "price", "size"]].astype({"timestamp": int, "price": float, "size": float})
        return df
