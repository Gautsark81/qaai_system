# qaai_system/infra/dhan_live.py
"""
DhanAdapterLive — minimal live adapter wrapper for Dhan REST API.

IMPORTANT:
- Replace endpoint paths and request/response mappings with the exact Dhan API spec.
- Keep this file separate from the sandbox so tests remain deterministic.
"""

from __future__ import annotations
from typing import Any, Dict, Tuple, Optional
import time
import logging
import requests
from qaai_system import env_config as cfg

logger = logging.getLogger("DhanAdapterLive")
logger.addHandler(logging.NullHandler())


class AuthenticationError(Exception):
    pass


class BrokerConnectionError(Exception):
    pass


class DhanAdapterLive:
    def __init__(
        self,
        client_id: Optional[str] = None,
        access_token: Optional[str] = None,
        base_url: Optional[str] = None,
        rate_limit_per_sec: float = 20.0,
        timeout: float = 8.0,
    ):
        self.client_id = client_id or cfg.DHAN_CLIENT_ID
        self.access_token = access_token or cfg.DHAN_ACCESS_TOKEN
        self.base_url = base_url or getattr(cfg, "DHAN_BASE_URL", "https://api.dhan.co")
        self.rate_limit_per_sec = rate_limit_per_sec
        self.timeout = timeout
        self._last_call_ts = 0.0
        self._session = requests.Session()
        self._session.headers.update(self._auth_headers())

    def _auth_headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        if self.client_id:
            headers["X-Client-Id"] = self.client_id
        return headers

    def _throttle(self) -> None:
        now = time.time()
        min_interval = 1.0 / max(1.0, self.rate_limit_per_sec)
        elapsed = now - self._last_call_ts
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_call_ts = time.time()

    def ping_broker(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Lightweight healthcheck. Returns (ok, payload_or_error).
        Uses a holdings/account endpoint as a minimal check.
        Replace '/v1/holdings' with the canonical Dhan health endpoint if available.
        """
        self._throttle()
        try:
            url = f"{self.base_url}/v1/holdings"  # <<--- confirm with Dhan docs
            resp = self._session.get(url, timeout=self.timeout)
            if resp.status_code in (401, 403):
                return False, {
                    "error": "authentication_failed",
                    "status": resp.status_code,
                    "body": resp.text,
                }
            resp.raise_for_status()
            return True, resp.json()
        except requests.RequestException as e:
            logger.exception("ping_broker failed")
            return False, {"error": "connection_failed", "detail": str(e)}

    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        order_meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Place an order and return a normalized dict:
          {"order_id", "status", "fill_price", "note"}
        Map keys from Dhan response into this dictionary.
        """
        self._throttle()
        payload = {
            # adapt payload keys to Dhan API
            "symbol": symbol,
            "side": side.upper(),
            "quantity": quantity,
            "price": price,
            "orderType": "LMT",
        }
        url = f"{self.base_url}/v1/orders"  # <<--- confirm path
        resp = self._session.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        # map Dhan response fields to your internal schema (adjust as needed)
        return {
            "order_id": data.get("order_id") or data.get("id"),
            "status": str(data.get("status", "OPEN")).upper(),
            "fill_price": data.get("avg_price") or data.get("fill_price"),
            "note": data,
        }

    def cancel_order(self, order_id: str) -> bool:
        self._throttle()
        url = f"{self.base_url}/v1/orders/{order_id}/cancel"  # <<--- confirm path
        resp = self._session.post(url, timeout=self.timeout)
        return resp.status_code in (200, 204)
