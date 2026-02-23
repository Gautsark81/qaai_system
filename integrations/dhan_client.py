"""
DhanHQ client (minimal, testable).

Provides:
- fetch_ohlcv(symbol, since=None, limit=100, timeframe='1m')
- get_top_nse_by_volume(limit=50)
Uses dependency injection for HTTP session so tests can monkeypatch.
Rate-limited by TokenBucket (infra.token_bucket).
"""
from typing import Optional, List, Dict, Any
import logging
import time
import requests

from infra.token_bucket import TokenBucket
from infra.fail_safe import fail_safe

logger = logging.getLogger(__name__)

DEFAULT_BASE = "https://api.dhan.co"  # placeholder

class DhanClient:
    def __init__(self, base_url: str = DEFAULT_BASE, session: Optional[requests.Session] = None,
                 token_bucket: Optional[TokenBucket] = None):
        self.base_url = base_url.rstrip('/')
        self.session = session or requests.Session()
        # default: allow 8 QPS as per Dhan constraints
        self.token_bucket = token_bucket or TokenBucket(capacity=8, refill_rate_per_sec=8.0)

    def _consume_token(self) -> bool:
        return self.token_bucket.consume(1)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self._consume_token():
            # mimic rate limit error
            logger.warning("rate limit: token not available")
            raise RuntimeError("rate_limited")
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.get(url, params=params or {}, timeout=5)
        resp.raise_for_status()
        return resp.json()

    @fail_safe(retries=2, backoff=0.2)
    def fetch_ohlcv(self, symbol: str, since: Optional[int] = None, limit: int = 200,
                    timeframe: str = "1m") -> List[Dict[str, Any]]:
        """
        Returns list of ohlcv dicts: {ts, open, high, low, close, volume}
        This method is safe for unit tests if session is mocked.
        """
        params = {"symbol": symbol, "limit": limit, "timeframe": timeframe}
        if since:
            params["since"] = int(since)
        data = self._get("/v1/market/ohlcv", params=params)
        # expected shape: {"data": [...]}
        return data.get("data", [])

    @fail_safe(retries=2, backoff=0.2)
    def get_top_nse_by_volume(self, limit: int = 50) -> List[str]:
        data = self._get("/v1/market/top-volume", params={"limit": limit})
        items = data.get("data", [])
        # return list of symbol strings
        return [it.get("symbol") for it in items if "symbol" in it]
