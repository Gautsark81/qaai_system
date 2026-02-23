# infra/dhan_client_sim.py
import time
import threading
import uuid
import random
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional, Any

@dataclass
class SimOrder:
    client_order_id: str
    symbol: str
    qty: float
    price: Optional[float]
    side: str
    status: str = "NEW"
    filled_qty: float = 0.0
    events: List[Dict[str, Any]] = field(default_factory=list)

class DhanClientSim:
    """
    Simple synchronous simulator for the Dhan trading client.

    Usage:
      sim = DhanClientSim(seed=42)
      oid = sim.place_order("NSE:XYZ", 10, 100.0, "BUY")
      sim.simulate_fill(oid, filled_qty=5)
      sim.simulate_fill(oid, filled_qty=5)
    """

    def __init__(self, seed: Optional[int] = None, default_latency_sec: float = 0.02):
        self.orders: Dict[str, SimOrder] = {}
        self.lock = threading.Lock()
        self.default_latency = default_latency_sec
        self.random = random.Random(seed)
        self.on_event: Optional[Callable[[str, dict], None]] = None
        # error injection
        self.error_rate = 0.0  # fraction of operations that fail
        self.disconnect_after = None  # order count after which client disconnects
        self._placed_count = 0

    def _maybe_delay(self):
        # small randomized latency to simulate network
        time.sleep(self.default_latency * self.random.uniform(0.5, 2.0))

    def _maybe_error(self):
        if self.random.random() < self.error_rate:
            raise RuntimeError("Simulated client error")

    def place_order(self, symbol: str, qty: float, price: Optional[float], side: str, client_order_id: Optional[str] = None) -> str:
        """Place a simulated order and return client_order_id"""
        self._maybe_delay()
        self._maybe_error()
        if client_order_id is None:
            client_order_id = f"sim-{uuid.uuid4().hex[:8]}"
        order = SimOrder(client_order_id=client_order_id, symbol=symbol, qty=qty, price=price, side=side)
        with self.lock:
            self.orders[client_order_id] = order
            self._placed_count += 1
            if self.disconnect_after and self._placed_count >= self.disconnect_after:
                # throw a disconnect error next time
                self.disconnect_after = None
                raise ConnectionError("Simulated disconnect after placing order")
        event = {"type": "ACK", "order_id": client_order_id, "status": "ACK"}
        order.events.append(event)
        if self.on_event:
            self.on_event(client_order_id, event)
        return client_order_id

    def cancel_order(self, client_order_id: str) -> bool:
        self._maybe_delay()
        self._maybe_error()
        with self.lock:
            if client_order_id not in self.orders:
                return False
            order = self.orders[client_order_id]
            if order.status in ("CANCELED", "FILLED"):
                return False
            order.status = "CANCELED"
            event = {"type": "CANCEL", "order_id": client_order_id, "status": "CANCELED"}
            order.events.append(event)
            if self.on_event:
                self.on_event(client_order_id, event)
            return True

    def simulate_fill(self, client_order_id: str, filled_qty: float, fill_price: Optional[float] = None):
        """Simulate a fill event (partial or full)."""
        self._maybe_delay()
        with self.lock:
            if client_order_id not in self.orders:
                raise KeyError("Order not found")
            order = self.orders[client_order_id]
            remaining = order.qty - order.filled_qty
            fill = min(remaining, filled_qty)
            order.filled_qty += fill
            if order.filled_qty >= order.qty - 1e-9:
                order.status = "FILLED"
            else:
                order.status = "PARTIALLY_FILLED"
            event = {
                "type": "FILL",
                "order_id": client_order_id,
                "filled_qty": fill,
                "total_filled": order.filled_qty,
                "fill_price": fill_price,
                "status": order.status,
            }
            order.events.append(event)
            if self.on_event:
                self.on_event(client_order_id, event)
            return event

    def get_order(self, client_order_id: str) -> SimOrder:
        with self.lock:
            return self.orders[client_order_id]

    def list_orders(self) -> List[SimOrder]:
        with self.lock:
            return list(self.orders.values())

    # Helpers for tests
    def set_error_rate(self, rate: float):
        """Set probability of random errors (0.0 - 1.0)."""
        self.error_rate = float(rate)

    def set_disconnect_after(self, n: int):
        """Force a disconnect after n placed orders (test only)."""
        self.disconnect_after = int(n)
