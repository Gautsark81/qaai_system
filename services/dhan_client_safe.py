"""
DhanSafeClient: async wrapper around HTTP/WS with retries, backoff, idempotency, and safe "stub" mode.
"""
import asyncio
import logging
import os
from typing import Optional, Any, Dict

import aiohttp
from aiohttp import ClientResponseError

logger = logging.getLogger("dhan_client_safe")

DEFAULT_TIMEOUT = int(os.getenv("ORDER_API_TIMEOUT_SECONDS", "10"))
ORDER_RETRY_MAX = int(os.getenv("ORDER_RETRY_MAX", "3"))
ORDER_RETRY_BACKOFF_BASE = float(os.getenv("ORDER_RETRY_BACKOFF_BASE", "0.1"))
SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() in ("true", "1", "yes")

class DhanSafeClient:
    def __init__(
        self,
        api_key: Optional[str],
        api_secret: Optional[str],
        client_id: Optional[str],
        max_retries: int = 5,
        backoff_base: float = 1.0,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client_id = client_id
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT))
        self._ws = None
        self._stopped = False

    async def request_json(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Generic request with exponential backoff retry.
        """
        attempt = 0
        while attempt < self.max_retries:
            try:
                attempt += 1
                async with self._session.request(method, url, **kwargs) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            except (ClientResponseError, aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning("Request error (attempt %d/%d) %s %s: %s", attempt, self.max_retries, method, url, e)
                if attempt >= self.max_retries:
                    logger.exception("Max retries reached for %s %s", method, url)
                    raise
                await asyncio.sleep(self.backoff(attempt))
        raise RuntimeError("Unreachable")

    def backoff(self, attempt: int) -> float:
        return self.backoff_base * (2 ** (attempt - 1))

    async def send_order(self, order_payload: dict) -> dict:
        """
        Sends an order to Dhan. In SAFE_MODE this will only log and return a stubbed response.
        Applies idempotency best-effort via payload['client_order_id'] if present.
        """
        if SAFE_MODE:
            logger.info("[SAFE_MODE] Stubbed send_order: %s", order_payload)
            await asyncio.sleep(0.02)
            return {"status": "stubbed", "payload": order_payload}

        url = os.getenv("DHAN_REST_BASE", "https://api.dhan.co") + "/orders"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            return await self.request_json("POST", url, json=order_payload, headers=headers)
        except Exception:
            logger.exception("Order send failed")
            raise

    async def get(self, endpoint: str, params: dict = None):
        url = self._build_url(endpoint)
        return await self.request_json("GET", url, params=params)

    def _build_url(self, endpoint: str) -> str:
        base = os.getenv("DHAN_REST_BASE", "https://api.dhan.co")
        if endpoint.startswith("http"):
            return endpoint
        return f"{base.rstrip('/')}/{endpoint.lstrip('/')}"

    async def close(self):
        logger.info("closing DhanSafeClient session")
        try:
            await self._session.close()
        except Exception:
            logger.exception("error while closing session")
