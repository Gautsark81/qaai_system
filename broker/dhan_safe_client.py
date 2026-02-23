# path: qaai_system/broker/dhan_safe_client.py
from __future__ import annotations

"""
DhanSafeClient

Production-ready safety wrapper around the raw DhanHQ client.

Features:
- Input validation
- Rate-limiting (simple sliding window)
- Safe retries with backoff
- Idempotent order placement via client_order_id
- Normalized error model via BrokerError / BrokerErrorType
- Structured logging hooks
"""

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Deque, Dict, Optional, Protocol, Tuple


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public Error Model
# ---------------------------------------------------------------------------

class BrokerErrorType(str, Enum):
    NETWORK = "NETWORK"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    VALIDATION = "VALIDATION"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class BrokerError(Exception):
    """Unified exception for all broker-related errors."""

    def __init__(
        self,
        type_: BrokerErrorType,
        message: str,
        raw: Optional[Exception] = None,
        payload: Optional[dict] = None,
    ) -> None:
        super().__init__(message)
        self.type = type_
        self.message = message
        self.raw = raw
        self.payload = payload or {}

    def __str__(self) -> str:  # pragma: no cover
        return f"[{self.type}] {self.message}"


# ---------------------------------------------------------------------------
# Configuration & Protocols
# ---------------------------------------------------------------------------

@dataclass
class DhanSafeConfig:
    client_id: str
    access_token: str

    max_retries: int = 3
    base_backoff_seconds: float = 0.5
    max_backoff_seconds: float = 3.0

    max_requests_per_sec: int = 10
    idempotency_ttl_seconds: int = 600
    log_order_payloads: bool = True
    logger_name: Optional[str] = None


class RawDhanClientProtocol(Protocol):
    def place_order(self, **kwargs: Any) -> dict: ...  # pragma: no cover
    def modify_order(self, **kwargs: Any) -> dict: ...  # pragma: no cover
    def cancel_order(self, **kwargs: Any) -> dict: ...  # pragma: no cover
    def get_order_by_id(self, order_id: str) -> dict: ...  # pragma: no cover
    def get_positions(self) -> dict: ...  # pragma: no cover
    def get_holdings(self) -> dict: ...  # pragma: no cover


@dataclass
class BrokerOrderResult:
    order_id: str
    status: str
    raw: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# DhanSafeClient Implementation
# ---------------------------------------------------------------------------

class DhanSafeClient:
    """
    Safety wrapper around the raw DhanHQ client.

    Usage:

        from dhanhq import dhanhq
        raw = dhanhq(client_id=cfg.client_id, access_token=cfg.access_token)
        safe = DhanSafeClient(config=cfg, raw_client=raw)

    Inject `safe` into ExecutionEngine / OrderManager instead of raw client.
    """

    def __init__(
        self,
        config: DhanSafeConfig,
        raw_client: RawDhanClientProtocol,
    ) -> None:
        self.config = config
        self.raw = raw_client

        self._logger = logging.getLogger(config.logger_name or __name__)
        self._lock = threading.Lock()
        self._request_timestamps: Deque[float] = deque()
        self._idempotency_cache: Dict[str, Tuple[float, BrokerOrderResult]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def place_order(
        self,
        client_order_id: str,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str,
        product_type: str,
        price: Optional[float] = None,
        validity: str = "DAY",
        **extra: Any,
    ) -> BrokerOrderResult:
        self._validate_basic_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
        )

        cached = self._get_cached_idempotent_result(client_order_id)
        if cached is not None:
            self._logger.debug(
                "DhanSafeClient: returning cached order for client_order_id=%s",
                client_order_id,
            )
            return cached

        payload = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "product_type": product_type,
            "price": price,
            "validity": validity,
            "client_order_id": client_order_id,
            **extra,
        }

        if self.config.log_order_payloads:
            self._logger.info(
                "Placing order: client_order_id=%s symbol=%s side=%s qty=%s "
                "type=%s product=%s extra=%s",
                client_order_id,
                symbol,
                side,
                quantity,
                order_type,
                product_type,
                {k: v for k, v in extra.items() if k != "sensitive"},
            )
        else:
            self._logger.info(
                "Placing order: client_order_id=%s symbol=%s side=%s qty=%s "
                "type=%s product=%s",
                client_order_id,
                symbol,
                side,
                quantity,
                order_type,
                product_type,
            )

        result: BrokerOrderResult = self._execute_with_retry(
            operation="place_order",
            func=self.raw.place_order,
            kwargs=self._map_place_order_payload(payload),
        )

        self._set_idempotent_result(client_order_id, result)
        return result

    def modify_order(
        self,
        order_id: str,
        client_order_id: Optional[str] = None,
        **kwargs: Any,
    ) -> BrokerOrderResult:
        self._logger.info(
            "Modifying order: order_id=%s client_order_id=%s kwargs=%s",
            order_id,
            client_order_id,
            kwargs,
        )

        if client_order_id:
            cached = self._get_cached_idempotent_result(client_order_id)
            if cached is not None:
                self._logger.debug(
                    "DhanSafeClient: returning cached modify result for client_order_id=%s",
                    client_order_id,
                )
                return cached

        payload = {"order_id": order_id, **kwargs}

        result: BrokerOrderResult = self._execute_with_retry(
            operation="modify_order",
            func=self.raw.modify_order,
            kwargs=self._map_modify_order_payload(payload),
        )

        if client_order_id:
            self._set_idempotent_result(client_order_id, result)

        return result

    def cancel_order(
        self,
        order_id: str,
        client_order_id: Optional[str] = None,
    ) -> BrokerOrderResult:
        self._logger.info(
            "Cancelling order: order_id=%s client_order_id=%s",
            order_id,
            client_order_id,
        )

        if client_order_id:
            cached = self._get_cached_idempotent_result(client_order_id)
            if cached is not None:
                self._logger.debug(
                    "DhanSafeClient: returning cached cancel result for client_order_id=%s",
                    client_order_id,
                )
                return cached

        payload = {"order_id": order_id}

        result: BrokerOrderResult = self._execute_with_retry(
            operation="cancel_order",
            func=self.raw.cancel_order,
            kwargs=self._map_cancel_order_payload(payload),
        )

        if client_order_id:
            self._set_idempotent_result(client_order_id, result)

        return result

    def get_order_by_id(self, order_id: str) -> BrokerOrderResult:
        raw = self._execute_with_retry(
            operation="get_order_by_id",
            func=self.raw.get_order_by_id,
            kwargs={"order_id": order_id},
            wrap=False,
        )
        return self._normalize_order(raw)

    def get_positions(self) -> dict:
        return self._execute_with_retry(
            operation="get_positions",
            func=self.raw.get_positions,
            kwargs={},
            wrap=False,
        )

    def get_holdings(self) -> dict:
        return self._execute_with_retry(
            operation="get_holdings",
            func=self.raw.get_holdings,
            kwargs={},
            wrap=False,
        )

    # ------------------------------------------------------------------
    # Validation / Rate-limit / Retry
    # ------------------------------------------------------------------

    def _validate_basic_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str,
        price: Optional[float],
    ) -> None:
        if not symbol or not isinstance(symbol, str):
            raise BrokerError(
                BrokerErrorType.VALIDATION,
                "Symbol must be a non-empty string",
            )

        side_upper = side.upper()
        if side_upper not in ("BUY", "SELL"):
            raise BrokerError(
                BrokerErrorType.VALIDATION,
                f"Invalid side={side}. Expected 'BUY' or 'SELL'.",
            )

        if quantity <= 0:
            raise BrokerError(
                BrokerErrorType.VALIDATION,
                f"Quantity must be positive, got {quantity}",
            )

        if order_type.upper() == "LIMIT" and (price is None or price <= 0):
            raise BrokerError(
                BrokerErrorType.VALIDATION,
                f"Limit order requires positive price, got {price}",
            )

    def _acquire_rate_limit_slot(self) -> None:
        with self._lock:
            now = time.time()
            window_start = now - 1.0
            while self._request_timestamps and self._request_timestamps[0] < window_start:
                self._request_timestamps.popleft()

            if len(self._request_timestamps) >= self.config.max_requests_per_sec:
                sleep_for = self._request_timestamps[0] + 1.0 - now
                if sleep_for > 0:
                    self._logger.debug("Rate-limit: sleeping for %.4fs", sleep_for)
                    time.sleep(sleep_for)

            self._request_timestamps.append(time.time())

    def _execute_with_retry(
        self,
        operation: str,
        func: Callable[..., Any],
        kwargs: dict,
        wrap: bool = True,
    ) -> Any:
        attempt = 0
        last_exc: Optional[Exception] = None

        while attempt <= self.config.max_retries:
            self._acquire_rate_limit_slot()
            try:
                self._logger.debug(
                    "DhanSafeClient: operation=%s attempt=%d kwargs=%s",
                    operation,
                    attempt,
                    kwargs,
                )
                raw = func(**kwargs)

                if wrap and operation in {"place_order", "modify_order", "cancel_order"}:
                    result = self._normalize_order(raw)
                else:
                    result = raw

                return result

            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                attempt += 1

                if attempt > self.config.max_retries:
                    self._logger.error(
                        "DhanSafeClient: operation=%s failed after %d attempts. exc=%r",
                        operation,
                        attempt - 1,
                        exc,
                    )
                    raise self._wrap_exception(operation, exc) from exc

                backoff = min(
                    self.config.base_backoff_seconds * (2 ** (attempt - 1)),
                    self.config.max_backoff_seconds,
                )
                self._logger.warning(
                    "DhanSafeClient: operation=%s attempt=%d failed; retrying in %.2fs. exc=%r",
                    operation,
                    attempt,
                    backoff,
                    exc,
                )
                time.sleep(backoff)

        raise BrokerError(
            BrokerErrorType.UNKNOWN,
            f"Operation {operation} failed for unknown reasons",
            raw=last_exc,
        )

    def _wrap_exception(self, operation: str, exc: Exception) -> BrokerError:
        msg = str(exc) or repr(exc)
        msg_lower = msg.lower()

        if "rate" in msg_lower and "limit" in msg_lower:
            err_type = BrokerErrorType.RATE_LIMIT
        elif "timeout" in msg_lower:
            err_type = BrokerErrorType.TIMEOUT
        elif "network" in msg_lower or "connection" in msg_lower:
            err_type = BrokerErrorType.NETWORK
        elif "invalid" in msg_lower or "validation" in msg_lower:
            err_type = BrokerErrorType.VALIDATION
        elif "rejected" in msg_lower:
            err_type = BrokerErrorType.REJECTED
        else:
            err_type = BrokerErrorType.UNKNOWN

        return BrokerError(
            err_type,
            f"{operation} failed: {msg}",
            raw=exc,
        )

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------

    def _map_place_order_payload(self, payload: dict) -> dict:
        return {
            "symbol": payload["symbol"],
            "transaction_type": payload["side"].upper(),
            "quantity": payload["quantity"],
            "order_type": payload["order_type"].upper(),
            "product_type": payload["product_type"],
            "validity": payload["validity"],
            "price": payload.get("price"),
            **{
                k: v
                for k, v in payload.items()
                if k
                not in {
                    "symbol",
                    "side",
                    "quantity",
                    "order_type",
                    "product_type",
                    "validity",
                    "price",
                }
            },
        }

    def _map_modify_order_payload(self, payload: dict) -> dict:
        return {
            "order_id": payload["order_id"],
            **{k: v for k, v in payload.items() if k != "order_id"},
        }

    def _map_cancel_order_payload(self, payload: dict) -> dict:
        return {"order_id": payload["order_id"]}

    def _normalize_order(self, raw: dict) -> BrokerOrderResult:
        if not isinstance(raw, dict):
            raise BrokerError(
                BrokerErrorType.UNKNOWN,
                f"Unexpected order response type: {type(raw)}",
                payload={"raw": raw},
            )

        order_id = str(
            raw.get("order_id")
            or raw.get("id")
            or raw.get("dhan_order_id")
            or "UNKNOWN"
        )
        status = str(raw.get("status") or raw.get("order_status") or "UNKNOWN")

        return BrokerOrderResult(
            order_id=order_id,
            status=status,
            raw=raw,
        )

    # ------------------------------------------------------------------
    # Idempotency Cache
    # ------------------------------------------------------------------

    def _get_cached_idempotent_result(
        self,
        client_order_id: str,
    ) -> Optional[BrokerOrderResult]:
        if not client_order_id:
            return None

        now = time.time()
        entry = self._idempotency_cache.get(client_order_id)
        if not entry:
            return None

        ts, result = entry
        if now - ts > self.config.idempotency_ttl_seconds:
            self._idempotency_cache.pop(client_order_id, None)
            return None

        return result

    def _set_idempotent_result(
        self,
        client_order_id: str,
        result: BrokerOrderResult,
    ) -> None:
        if not client_order_id:
            return

        now = time.time()
        self._idempotency_cache[client_order_id] = (now, result)
        self._cleanup_idempotency_cache(now)

    def _cleanup_idempotency_cache(self, now: Optional[float] = None) -> None:
        if now is None:
            now = time.time()

        ttl = self.config.idempotency_ttl_seconds
        for key, (ts, _) in list(self._idempotency_cache.items()):
            if now - ts > ttl:
                self._idempotency_cache.pop(key, None)
