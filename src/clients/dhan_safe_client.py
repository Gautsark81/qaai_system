# Path: src/clients/dhan_safe_client.py
"""
DhanSafeClient

Synchronous safe client wrapping Dhan API endpoints with:
- typed exceptions
- exponential backoff retries
- retry budget
- circuit breaker
- structured logging

Designed to be injected where needed. It is synchronous on purpose; if
you need asyncio integration, call it via run_in_executor or I can add async wrappers.
"""
from __future__ import annotations

import time
import threading
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Callable
import requests

logger = logging.getLogger("src.clients.dhan_safe_client")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)


# Exceptions
class DhanClientError(Exception):
    pass

class RateLimitError(DhanClientError):
    def __init__(self, message: str = "rate limited", retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after

class NetworkError(DhanClientError):
    pass

class DhanValidationError(DhanClientError):
    pass

class CircuitOpenError(DhanClientError):
    pass


# Circuit breaker
class CircuitBreaker:
    def __init__(self, fail_threshold: int = 5, reset_timeout: int = 60):
        self.fail_threshold = fail_threshold
        self.reset_timeout = reset_timeout
        self.fail_count = 0
        self._lock = threading.Lock()
        self.opened_at: Optional[float] = None

    def record_success(self):
        with self._lock:
            self.fail_count = 0
            self.opened_at = None

    def record_failure(self):
        with self._lock:
            self.fail_count += 1
            if self.fail_count >= self.fail_threshold:
                self.opened_at = time.time()
                logger.warning("Circuit opened (fail_count=%d)", self.fail_count)

    def is_open(self) -> bool:
        with self._lock:
            if self.opened_at is None:
                return False
            if time.time() - self.opened_at > self.reset_timeout:
                logger.info("Circuit moving to half-open (reset timeout passed)")
                self.fail_count = 0
                self.opened_at = None
                return False
            return True


@dataclass
class SafeResponse:
    success: bool
    data: Optional[Dict[str, Any]] = None
    raw: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def default_request(method: str, url: str, headers: Dict[str, str], json: Optional[Dict] = None, timeout: int = 10):
    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


class DhanSafeClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.dhan.co",
        max_retries: int = 4,
        backoff_factor: float = 0.5,
        retry_budget: int = 20,
        circuit_fail_threshold: int = 6,
        circuit_reset_timeout: int = 60,
        requester: Callable = default_request,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_budget = retry_budget
        self._budget_lock = threading.Lock()
        self._circuit = CircuitBreaker(circuit_fail_threshold, circuit_reset_timeout)
        self.requester = requester

    def _consume_budget(self) -> bool:
        with self._budget_lock:
            if self.retry_budget <= 0:
                return False
            self.retry_budget -= 1
            return True

    def _log_call(self, action: str, params: Dict[str, Any], raw_request: Dict[str, Any], raw_response: Optional[Dict[str, Any]], error: Optional[str]):
        # keep structured but don't log secrets
        logger.info("action=%s params=%s error=%s", action, params, error)

    def _request(self, method: str, path: str, payload: Optional[Dict] = None) -> SafeResponse:
        if self._circuit.is_open():
            raise CircuitOpenError("Circuit is open; skipping request")

        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        last_error: Optional[str] = None
        for attempt in range(1, self.max_retries + 1):
            if attempt > 1:
                if not self._consume_budget():
                    last_error = "retry-budget-exhausted"
                    break

            try:
                raw_req = {"method": method, "url": url, "payload": payload}
                logger.debug("Request attempt %d: %s", attempt, raw_req)
                resp = self.requester(method, url, headers=headers, json=payload)

                status = getattr(resp, "status_code", None)
                text = getattr(resp, "text", None)
                try:
                    body = resp.json()
                except Exception:
                    body = {"raw_text": text}

                raw_resp = {"status": status, "body": body, "headers": getattr(resp, "headers", {})}

                if status and 200 <= status < 300:
                    self._circuit.record_success()
                    self._log_call(path, payload or {}, raw_req, raw_resp, None)
                    return SafeResponse(success=True, data=body, raw=raw_resp)

                if status == 429:
                    retry_after = None
                    try:
                        retry_after = int(resp.headers.get("Retry-After")) if hasattr(resp, "headers") else None
                    except Exception:
                        retry_after = None
                    last_error = f"rate_limited(retry_after={retry_after})"
                    logger.warning("Rate limited; attempt=%d retry_after=%s", attempt, retry_after)
                    if retry_after:
                        time.sleep(retry_after)
                    else:
                        time.sleep(self.backoff_factor * (2 ** (attempt - 1)))
                    continue

                if status and 500 <= status < 600:
                    last_error = f"server_error({status})"
                    logger.warning("Server error %s; attempt=%d", status, attempt)
                    time.sleep(self.backoff_factor * (2 ** (attempt - 1)))
                    continue

                if status and 400 <= status < 500:
                    self._circuit.record_failure()
                    err_msg = body.get("error") if isinstance(body, dict) else str(body)
                    self._log_call(path, payload or {}, raw_req, raw_resp, err_msg)
                    raise DhanValidationError(f"Validation error: {err_msg}")

                last_error = f"unknown_status_{status}"
                time.sleep(self.backoff_factor * (2 ** (attempt - 1)))

            except DhanValidationError:
                raise
            except CircuitOpenError:
                raise
            except Exception as ex:
                last_error = str(ex)
                logger.exception("Network/Request error on attempt %d", attempt)
                time.sleep(self.backoff_factor * (2 ** (attempt - 1)))
                continue

        self._circuit.record_failure()
        self._log_call(path, payload or {}, {"method": method, "url": url}, None, last_error)
        raise NetworkError(f"Request failed after retries; last_error={last_error}")

    # Safe wrappers
    def safe_place_order(self, order_payload: Dict[str, Any]) -> SafeResponse:
        try:
            res = self._request("POST", "/v1/orders", order_payload)
            return res
        except DhanValidationError as e:
            logger.error("Validation error in place_order: %s", e)
            return SafeResponse(success=False, error=str(e))
        except RateLimitError as e:
            logger.warning("Rate limited placing order: %s", e)
            return SafeResponse(success=False, error=str(e))
        except DhanClientError as e:
            logger.error("Dhan client error placing order: %s", e)
            return SafeResponse(success=False, error=str(e))

    def safe_modify_order(self, order_id: str, modify_payload: Dict[str, Any]) -> SafeResponse:
        try:
            path = f"/v1/orders/{order_id}"
            return self._request("PUT", path, modify_payload)
        except DhanClientError as e:
            logger.error("modify_order error: %s", e)
            return SafeResponse(success=False, error=str(e))

    def safe_cancel_order(self, order_id: str) -> SafeResponse:
        try:
            path = f"/v1/orders/{order_id}/cancel"
            return self._request("POST", path, {})
        except DhanClientError as e:
            logger.error("cancel_order error: %s", e)
            return SafeResponse(success=False, error=str(e))

    def safe_get_positions(self) -> SafeResponse:
        try:
            return self._request("GET", "/v1/positions")
        except DhanClientError as e:
            logger.error("get_positions error: %s", e)
            return SafeResponse(success=False, error=str(e))

    def safe_get_holdings(self) -> SafeResponse:
        try:
            return self._request("GET", "/v1/holdings")
        except DhanClientError as e:
            logger.error("get_holdings error: %s", e)
            return SafeResponse(success=False, error=str(e))

    def safe_get_margins(self) -> SafeResponse:
        try:
            return self._request("GET", "/v1/margins")
        except DhanClientError as e:
            logger.error("get_margins error: %s", e)
            return SafeResponse(success=False, error=str(e))

    def safe_get_quote(self, symbol: str) -> SafeResponse:
        try:
            path = f"/v1/quote/{symbol}"
            return self._request("GET", path)
        except DhanClientError as e:
            logger.error("get_quote error: %s", e)
            return SafeResponse(success=False, error=str(e))
