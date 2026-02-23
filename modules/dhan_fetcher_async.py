# modules/dhan_fetcher_async.py
import asyncio
import time
from typing import Optional, Dict, Any
import aiohttp


class AsyncRateLimiter:
    """
    Simple async token bucket (not perfect high-perf but good for typical fetchers).
    capacity: max tokens
    refill_rate: tokens per second
    """
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self._tokens = float(capacity)
        self._last = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()

    async def _refill(self):
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last
        if elapsed <= 0:
            return
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
        self._last = now

    async def wait(self, tokens: float = 1.0):
        while True:
            async with self._lock:
                await self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                missing = tokens - self._tokens
                wait_seconds = max((missing / self.refill_rate), 0.01)
            await asyncio.sleep(wait_seconds)


class DhanFetcherAsync:
    def __init__(self,
                 api_key: str,
                 base_url: str = "https://api.dhan.com",
                 rate_limiter: Optional[AsyncRateLimiter] = None,
                 max_concurrency: int = 5,
                 session: Optional[aiohttp.ClientSession] = None):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.rate_limiter = rate_limiter or AsyncRateLimiter(capacity=10, refill_rate=2)
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._own_session = session is None
        self.session = session or aiohttp.ClientSession()

    async def close(self):
        if self._own_session:
            await self.session.close()

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "qaai_system/dhan_fetcher_async/1.0"
        }

    async def request(self, method: str, path: str, params=None, json=None, headers: Dict[str, str] = None, timeout: float = 10.0):
        url = f"{self.base_url}/{path.lstrip('/')}"
        hdrs = self._headers()
        if headers:
            hdrs.update(headers)

        attempt = 0
        max_attempts = 6

        async with self._semaphore:
            # wait for rate-limiter token
            await self.rate_limiter.wait(tokens=1.0)
            while attempt < max_attempts:
                attempt += 1
                try:
                    async with self.session.request(method, url, params=params, json=json, headers=hdrs, timeout=timeout) as resp:
                        status = resp.status
                        if status == 429:
                            ra = resp.headers.get("Retry-After")
                            if ra:
                                try:
                                    wait = float(ra)
                                except ValueError:
                                    wait = 5.0
                            else:
                                wait = min(60, (2 ** attempt) * 0.5)
                            await asyncio.sleep(wait)
                            continue
                        if 500 <= status < 600:
                            wait = min(60, (2 ** attempt) * 0.5)
                            await asyncio.sleep(wait)
                            continue
                        # final: parse
                        text = await resp.text()
                        try:
                            j = await resp.json()
                        except Exception:
                            j = None
                        return {"status_code": status, "json": j, "text": text, "headers": dict(resp.headers)}
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    wait = min(60, (2 ** attempt) * 0.5)
                    await asyncio.sleep(wait)
                    continue

        raise RuntimeError(f"Max attempts exceeded for {method} {url}")
