# clients/order_manager.py
"""
Order Manager - wraps a DhanSafeClient and provides:
- idempotent place_order using idempotency_key (pluggable store)
- retries on transient errors with exponential backoff
- in-memory/local order cache for quick status checks (optionally persisted)
- cancel and get_status helpers that unify client responses and local cache
- emits lightweight metrics (orders_placed, orders_failed) if metrics module available
- optional persistent_order_store for order cache durability (must implement save_order(order_id, metadata), load_all())
"""

from __future__ import annotations
import threading
import time
import uuid
import logging
from typing import Dict, Any, Optional
import random

logger = logging.getLogger(__name__)

# optional metrics (best-effort import)
try:
    from clients import metrics as metrics_module  # type: ignore
except Exception:
    metrics_module = None


class OrderManager:
    def __init__(
        self,
        client,
        max_retries: int = 3,
        backoff_base: float = 0.05,
        backoff_jitter: float = 0.02,
        idempotency_store: Optional[Dict[str, Dict[str, Any]]] = None,
        persistent_order_store: Optional[Any] = None,
    ):
        """
        persistent_order_store: optional object implementing:
           - save_order(order_id: str, metadata: dict)
           - load_all() -> dict(order_id -> metadata)
           - delete_order(order_id) [optional]
        """
        self.client = client
        self.max_retries = int(max_retries)
        self.backoff_base = float(backoff_base)
        self.backoff_jitter = float(backoff_jitter)
        self._idempotency_store = idempotency_store if idempotency_store is not None else {}
        self.persistent_order_store = persistent_order_store
        # local order cache: order_id -> order_metadata (in-memory)
        self._orders: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

        # load persisted orders if provided
        if self.persistent_order_store is not None:
            try:
                persisted = self.persistent_order_store.load_all()
                if isinstance(persisted, dict):
                    self._orders.update(persisted)
            except Exception:
                logger.exception("Failed to load persisted orders from persistent_order_store")

    def _sleep_backoff(self, attempt: int):
        backoff = (2 ** (attempt - 1)) * self.backoff_base
        jitter = (random.random() * 2 - 1) * self.backoff_jitter
        to_sleep = max(0.0, backoff + jitter)
        time.sleep(to_sleep)

    def _persist_order_local(self, order_id: str, meta: Dict[str, Any]):
        if self.persistent_order_store is None:
            return
        try:
            self.persistent_order_store.save_order(order_id, meta)
        except Exception:
            logger.exception("Failed to persist order %s", order_id)

    def place_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: Optional[float] = None,
        order_type: str = "LIMIT",
        idempotency_key: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        if idempotency_key is None:
            idempotency_key = str(uuid.uuid4())

        # Quick-path: check idempotency store (store is canonical)
        try:
            if idempotency_key in self._idempotency_store:
                stored = dict(self._idempotency_store.get(idempotency_key))
                logger.debug("Idempotency hit for key %s -> order %s", idempotency_key, stored.get("order_id"))
                return stored
        except Exception:
            logger.exception("Idempotency store lookup failed; continuing to place order")

        attempt = 0
        last_exc = None
        while attempt < max(1, self.max_retries):
            attempt += 1
            try:
                resp = self.client.place_order(symbol=symbol, side=side, qty=qty, price=price, order_type=order_type, **kwargs)
                order_id = resp.get("order_id") or resp.get("id") or str(uuid.uuid4())
                meta = {
                    "order_id": order_id,
                    "symbol": symbol,
                    "side": side,
                    "qty": float(qty),
                    "price": float(price) if price is not None else None,
                    "type": order_type,
                    "status": resp.get("status", "NEW"),
                    "created_at": resp.get("created_at", time.time()),
                    "raw": resp,
                    "idempotency_key": idempotency_key,
                }
                with self._lock:
                    try:
                        self._idempotency_store[idempotency_key] = meta
                    except Exception:
                        logger.exception("Failed to persist idempotency mapping to store")
                    self._orders[order_id] = meta

                # persist to persistent_order_store if provided
                try:
                    self._persist_order_local(order_id, meta)
                except Exception:
                    logger.exception("Failed to persist local order after placing")

                # metrics
                try:
                    if metrics_module is not None and hasattr(metrics_module, "orders_placed"):
                        metrics_module.orders_placed.inc()
                except Exception:
                    logger.exception("Failed to increment orders_placed metric")

                return meta
            except Exception as exc:
                last_exc = exc
                logger.warning("place_order attempt %d failed for %s %s: %s", attempt, side, symbol, exc)
                if attempt >= self.max_retries:
                    try:
                        if metrics_module is not None and hasattr(metrics_module, "orders_failed"):
                            metrics_module.orders_failed.inc()
                    except Exception:
                        logger.exception("Failed to increment orders_failed metric")
                    logger.exception("Max retries reached for place_order %s %s", side, symbol)
                    raise
                self._sleep_backoff(attempt)
        raise RuntimeError("place_order failed") from last_exc

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        resp = self.client.cancel_order(order_id)
        with self._lock:
            meta = self._orders.get(order_id, {})
            meta["status"] = resp.get("status", "CANCELLED")
            meta["cancelled_at"] = resp.get("cancelled_at", time.time())
            meta["raw_cancel"] = resp
            self._orders[order_id] = meta
        # persist change
        try:
            self._persist_order_local(order_id, self._orders[order_id])
        except Exception:
            logger.exception("Failed to persist order cancellation")
        return meta

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        try:
            resp = self.client.get_order_status(order_id)
        except Exception:
            with self._lock:
                return dict(self._orders.get(order_id, {}))
        with self._lock:
            meta = self._orders.get(order_id, {})
            meta.update({"status": resp.get("status", meta.get("status")), "raw_status": resp})
            self._orders[order_id] = meta
        # persist updated status
        try:
            self._persist_order_local(order_id, self._orders[order_id])
        except Exception:
            logger.exception("Failed to persist order status update")
        return dict(meta)

    def list_local_orders(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return dict(self._orders)

    def lookup_by_idempotency_key(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            val = self._idempotency_store.get(key)
            return dict(val) if val is not None else None
        except Exception:
            return None
