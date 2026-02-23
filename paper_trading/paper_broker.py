# File: qaai_system/paper_trading/paper_broker.py
import uuid
import time
from typing import List, Dict, Optional


class PaperExecutionProvider:
    """
    Supercharged paper broker.
    - Immediate or delayed fills
    - Tracks open/filled/cancelled orders
    - Supports kill switch & cancel-all
    - Tracks realized PnL per symbol
    """

    def __init__(self, instant_fill: bool = True, fill_delay: float = 0.0):
        self.instant_fill = instant_fill
        self.fill_delay = fill_delay
        self.kill_switch = False

        # State
        self.orders: Dict[str, Dict] = {}  # all orders by id
        self.realized_pnl: Dict[str, float] = {}  # per-symbol realized PnL
        self.order_log: List[Dict] = []  # historical reports

    # ----------------------------
    # Core API
    # ----------------------------
    def place_orders(self, orders: List[Dict]) -> List[Dict]:
        if self.kill_switch:
            return [
                {
                    "status": "REJECTED",
                    "reason": "KILL_SWITCH_ACTIVE",
                    "symbol": o["symbol"],
                    "side": o["side"],
                    "qty": o.get("qty", 1),
                }
                for o in orders
            ]

        reports = []
        for order in orders:
            oid = str(uuid.uuid4())
            now = time.time()
            qty = float(order.get("qty", 1))
            price = float(order.get("price", order.get("market_price", 100.0)))

            base = {
                "order_id": oid,
                "symbol": order["symbol"],
                "side": order["side"].upper(),
                "qty": qty,
                "price": price,
                "timestamp": now,
                "status": "OPEN",
                "realized_pnl": 0.0,
                "notional": qty * price,
            }

            if self.instant_fill:
                base["status"] = "FILLED"
                base["fill_time"] = now + self.fill_delay
                # Simplified PnL logic: buy reduces pnl, sell adds pnl
                pnl = qty * (price if base["side"] == "SELL" else -price)
                self.realized_pnl[base["symbol"]] = (
                    self.realized_pnl.get(base["symbol"], 0.0) + pnl
                )
                base["realized_pnl"] = pnl

            self.orders[oid] = base
            self.order_log.append(base.copy())
            reports.append(base)

        return reports

    def cancel_order(self, order_id: str) -> Optional[Dict]:
        order = self.orders.get(order_id)
        if not order or order["status"] != "OPEN":
            return None
        order["status"] = "CANCELLED"
        self.order_log.append(order.copy())
        return order

    def cancel_all(self) -> List[Dict]:
        cancelled = []
        for oid, order in list(self.orders.items()):
            if order["status"] == "OPEN":
                order["status"] = "CANCELLED"
                self.order_log.append(order.copy())
                cancelled.append(order)
        return cancelled

    # ----------------------------
    # Risk controls
    # ----------------------------
    def activate_kill_switch(self):
        """Block new orders, cancel open ones."""
        self.kill_switch = True
        self.cancel_all()

    def deactivate_kill_switch(self):
        self.kill_switch = False

    # ----------------------------
    # Reporting
    # ----------------------------
    def get_open_orders(self) -> List[Dict]:
        return [o for o in self.orders.values() if o["status"] == "OPEN"]

    def get_filled_orders(self) -> List[Dict]:
        return [o for o in self.orders.values() if o["status"] == "FILLED"]

    def get_realized_pnl(self, symbol: Optional[str] = None) -> float:
        if symbol:
            return self.realized_pnl.get(symbol, 0.0)
        return sum(self.realized_pnl.values())
