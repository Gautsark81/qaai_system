# clients/dhan_safe_client.py
import threading
import time
import uuid
from typing import Dict, Any, Optional


class DhanSafeClient:
    """
    Minimal 'safe' client useful for unit tests and safe-mode operation.
    If safe_mode=True, send_order will emulate immediate fill (status 'filled').
    Otherwise we create an order record with status 'NEW'.
    """

    def __init__(self, safe_mode: bool = False):
        self.safe_mode = safe_mode
        self._orders: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def send_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Emulate sending order to the broker.
        When safe_mode=True, we simulate an immediate filled order (status 'filled').
        Otherwise we create an order record with status 'NEW'.
        Returns order metadata including 'order_id' and 'status'.
        """
        with self._lock:
            order_id = order.get("order_id") or f"order-{uuid.uuid4().hex[:12]}"
            now = time.time()
            base = {
                "order_id": order_id,
                "symbol": order.get("symbol"),
                "qty": order.get("qty"),
                "price": order.get("price"),
                "side": order.get("side"),
                "created_ts": now,
                # when safe_mode True tests expect 'filled' lowercase
                "status": "filled" if self.safe_mode else "NEW",
            }
            self._orders[order_id] = base.copy()
            return base

    def _get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Internal helper used in unit tests to inspect stored orders.
        Returns a copy of the stored order dict or None if not present.
        """
        with self._lock:
            o = self._orders.get(order_id)
            return dict(o) if o is not None else None

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order. If order doesn't exist, return not_found dict (lowercase 'not_found').
        For existing order, update status to 'cancelled' and return metadata.
        """
        with self._lock:
            if order_id not in self._orders:
                return {"order_id": order_id, "status": "not_found"}
            self._orders[order_id]["status"] = "cancelled"
            self._orders[order_id]["cancelled_ts"] = time.time()
            return dict(self._orders[order_id])

    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Return stored order metadata if present, otherwise None.
        """
        with self._lock:
            o = self._orders.get(order_id)
            return dict(o) if o is not None else None


class MockDhanSafeClient(DhanSafeClient):
    """
    Mock client used by tests. It uses uppercase status tokens for 'NEW' and 'CANCELLED'
    to match test assertions, and provides a synchronous place_order wrapper.
    """

    def __init__(self):
        # For tests we usually want to simulate orders that start NEW then can be cancelled.
        # Use safe_mode=False so send_order returns 'NEW' (we convert to uppercase here).
        super().__init__(safe_mode=False)

    # tests expect a place_order() method signature
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
        """
        Test-friendly wrapper that returns an order meta dict with uppercase status "NEW".
        """
        order = {
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "price": price,
            "order_type": order_type,
            "idempotency_key": idempotency_key,
        }
        meta = super().send_order(order)
        # normalize for tests that expect uppercase status "NEW"
        meta["status"] = "NEW"
        # store uppercase status in internal map to preserve cancel semantics below
        with self._lock:
            self._orders[meta["order_id"]] = dict(meta)
        return meta

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        with self._lock:
            if order_id not in self._orders:
                raise KeyError(f"order {order_id} not found")
            # tests expect uppercase tokens for Mock
            m = dict(self._orders[order_id])
            s = m.get("status", "")
            if isinstance(s, str):
                m["status"] = s.upper()
            return m

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        with self._lock:
            if order_id not in self._orders:
                return {"order_id": order_id, "status": "NOT_FOUND"}
            self._orders[order_id]["status"] = "CANCELLED"
            self._orders[order_id]["cancelled_ts"] = time.time()
            return dict(self._orders[order_id])
