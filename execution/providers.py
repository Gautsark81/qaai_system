# File: qaai_system/execution/providers.py
from __future__ import annotations
import logging
from typing import Dict, Any, Optional, List


class BaseExecutionProvider:
    def __init__(self, pm_method: str = "fifo"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._order_id_counter = 1
        self._orders: Dict[str, Dict[str, Any]] = {}
        self._positions: Dict[str, float] = {}
        self._trade_log: List[Dict[str, Any]] = []
        self._lots: Dict[str, List[tuple]] = {}
        self._pm_method = pm_method.lower()
        self._account_nav: float = 1_000_000.0

    def _next_id(self) -> str:
        oid = f"order_{self._order_id_counter}"
        self._order_id_counter += 1
        return oid

    # ---------------- Order lifecycle ----------------
    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        order_id = self._next_id()
        order = dict(order)

        # required fields
        order["order_id"] = order_id
        order["symbol"] = order.get("symbol", "unknown")
        order["status"] = "filled"
        order["filled_qty"] = int(order.get("qty") or order.get("quantity") or 0)
        order["avg_price"] = float(order.get("price", 0.0) or 0.0)

        # save
        self._orders[order_id] = order
        self._update_positions(order)
        return order

    def cancel_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        order = self._orders.get(order_id)
        if not order:
            return None
        if order.get("status") not in {"filled", "CANCELLED"}:
            order["status"] = "CANCELLED"
        self._orders[order_id] = order
        return order

    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        return self._orders.get(order_id)

    # ---------------- Positions & PnL ----------------
    def get_positions(self) -> Dict[str, float]:
        return dict(self._positions)

    def _update_positions(self, order: Dict[str, Any]):
        symbol = order["symbol"]
        qty = int(order.get("qty") or order.get("quantity", 0))
        side = order.get("side")
        price = float(order.get("price", 0.0) or 0.0)

        if side == "buy":
            self._positions[symbol] = self._positions.get(symbol, 0) + qty
            if self._pm_method == "fifo":
                self._lots.setdefault(symbol, []).append((qty, price))
            elif self._pm_method == "avg":
                old_qty = self._positions.get(symbol, 0)
                old_cost = getattr(self, "_avg_cost", {}).get(symbol, 0.0)
                new_qty = old_qty + qty
                avg_cost = (
                    (old_qty * old_cost + qty * price) / new_qty
                    if new_qty > 0
                    else price
                )
                if not hasattr(self, "_avg_cost"):
                    self._avg_cost = {}
                self._avg_cost[symbol] = avg_cost

        elif side == "sell":
            self._positions[symbol] = self._positions.get(symbol, 0) - qty
            pnl = 0.0
            if self._pm_method == "fifo":
                lots = self._lots.get(symbol, [])
                remain = qty
                new_lots = []
                for lqty, lpx in lots:
                    if remain <= 0:
                        new_lots.append((lqty, lpx))
                        continue
                    if lqty <= remain:
                        pnl += (price - lpx) * lqty
                        remain -= lqty
                    else:
                        pnl += (price - lpx) * remain
                        new_lots.append((lqty - remain, lpx))
                        remain = 0
                self._lots[symbol] = new_lots
            elif self._pm_method == "avg" and hasattr(self, "_avg_cost"):
                avg_cost = self._avg_cost.get(symbol, price)
                pnl = (price - avg_cost) * qty

            self._trade_log.append(
                {
                    "symbol": symbol,
                    "pnl": pnl,
                    "order_id": order["order_id"],
                    "qty": qty,
                    "price": price,
                }
            )

    def get_trade_log(self) -> List[Dict[str, Any]]:
        return list(self._trade_log)


class PaperExecutionProvider(BaseExecutionProvider):
    """Paper trading provider - instant fills"""

    pass


class LiveExecutionProvider(BaseExecutionProvider):
    """Live provider (stub) - can be extended to real API"""

    pass
