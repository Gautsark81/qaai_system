# modules/data_pipeline/providers/dhan_http_fetcher.py
from __future__ import annotations
import time
import random
from typing import Optional, Dict, Any
from urllib.parse import urljoin
import requests
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HTTPFetchError(RuntimeError):
    pass


class DhanHTTPFetcher:
    """
    HTTP fetcher for Dhan-like REST endpoints.

    Usage:
        f = DhanHTTPFetcher(base_url="https://api.dhan.co", api_key="...", max_retries=4)
        df = f.fetch_ohlcv("RELIANCE", "2023-01-01", "2023-03-01", timeframe="1d")
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        max_retries: int = 4,
        backoff_factor: float = 0.5,
        session: Optional[requests.Session] = None,
        timeout: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/") + "/"
        self.api_key = api_key
        self.max_retries = int(max_retries)
        self.backoff_factor = float(backoff_factor)
        self.timeout = timeout
        self.session = session or requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        self.session.headers.update({"User-Agent": "qaai-system/1.0 (+https://example)"})

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = urljoin(self.base_url, path.lstrip("/"))
        tries = 0
        last_exc = None
        while tries <= self.max_retries:
            tries += 1
            try:
                resp = self.session.request(method, url, params=params, timeout=self.timeout)
                if resp.status_code == 429:
                    # Rate-limited — respect Retry-After where possible
                    ra = resp.headers.get("Retry-After")
                    if ra:
                        try:
                            wait = float(ra)
                        except Exception:
                            wait = self.backoff_factor * tries
                        logger.warning("Rate limited, sleeping retry-after=%s", wait)
                        time.sleep(wait)
                        continue
                    # fallback to exponential backoff with jitter
                    backoff = self.backoff_factor * (2 ** (tries - 1))
                    jitter = random.random() * 0.1 * backoff
                    time.sleep(backoff + jitter)
                    continue
                if 500 <= resp.status_code <= 599:
                    # server error, retry with backoff
                    backoff = self.backoff_factor * (2 ** (tries - 1))
                    time.sleep(backoff + random.random() * 0.1 * backoff)
                    continue
                if not resp.ok:
                    raise HTTPFetchError(f"HTTP {resp.status_code} for {url}: {resp.text[:200]}")
                return resp.json()
            except (requests.RequestException, ValueError) as exc:
                last_exc = exc
                backoff = self.backoff_factor * (2 ** (tries - 1))
                time.sleep(backoff + random.random() * 0.1 * backoff)
                continue
        raise HTTPFetchError(f"Failed after {self.max_retries} retries; last error: {last_exc}")

    def fetch_ohlcv(self, symbol: str, start: str, end: str, timeframe: str = "1d") -> pd.DataFrame:
        """
        Calls an endpoint that returns OHLCV for a symbol and returns a DataFrame indexed by timestamp.
        The exact JSON schema may vary — here we support commonly returned shapes:
        - {"data": [{"timestamp": "...", "open":.., "high":.., "low":.., "close":.., "volume":..}, ...]}
        - {"ohlcv": {"timestamps":[...], "open":[...], ...}}
        """
        params = {"symbol": symbol, "start": start, "end": end, "timeframe": timeframe}
        payload = self._request("GET", "/v2/ohlcv", params=params)
        # Try shape 1: payload["data"] list of dicts
        if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], list):
            rows = payload["data"]
            df = pd.DataFrame(rows)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.set_index("timestamp")
            # normalize names
            df = df.rename(columns={
                "volume": "volume", "open": "open", "high": "high", "low": "low", "close": "close"
            })
            # Ensure columns exist
            for c in ("open", "high", "low", "close", "volume"):
                if c not in df.columns:
                    df[c] = pd.NA
            return df[["open", "high", "low", "close", "volume"]].astype(float)
        # Try shape 2: "ohlcv" block of lists
        if isinstance(payload, dict) and "ohlcv" in payload and isinstance(payload["ohlcv"], dict):
            o = payload["ohlcv"]
            idx = pd.to_datetime(o.get("timestamps", []))
            df = pd.DataFrame({
                "open": o.get("open", []),
                "high": o.get("high", []),
                "low": o.get("low", []),
                "close": o.get("close", []),
                "volume": o.get("volume", []),
            }, index=idx)
            df.index.name = "timestamp"
            return df.astype(float)
        # Fallback: if API returns a single dictionary mapping
        if isinstance(payload, dict) and all(k in payload for k in ("timestamps", "open", "high", "low", "close", "volume")):
            idx = pd.to_datetime(payload["timestamps"])
            df = pd.DataFrame({
                "open": payload["open"],
                "high": payload["high"],
                "low": payload["low"],
                "close": payload["close"],
                "volume": payload["volume"],
            }, index=idx)
            df.index.name = "timestamp"
            return df.astype(float)
        raise HTTPFetchError("Unsupported OHLCV payload shape")

    def fetch_fundamentals(self, symbol: str) -> Dict[str, Any]:
        params = {"symbol": symbol}
        payload = self._request("GET", "/v2/fundamentals", params=params)
        # expect a dict with fundamentals
        if isinstance(payload, dict):
            # normalise a few fields
            payload.setdefault("symbol", symbol)
            return payload
        raise HTTPFetchError("Unsupported fundamentals payload")
