# execution/broker_adapter.py
"""
BrokerAdapter — improved & test-friendly

Features:
- Paper and Dhan (live) modes (DhanAdapter fallback preserved)
- Non-blocking fill callback registration for ExecutionEngine.on_fill
- Async simulated fills in paper mode (threading)
- Order / position tracking and normalized fill events
- Improved SL/TP check helper
"""

import logging
import random
import threading
import time
from typing import Optional, Callable, Dict, Any, List

# Optional import for live integration
try:
    from infra.dhan_adapter import DhanAdapter  # may raise ImportError in tests
except Exception:
    DhanAdapter = None

logger = logging.getLogger("BrokerAdapter")
logger.setLevel(logging.INFO)


class BrokerAdapter:
    def __init__(self, mode: str = "paper"):
        """
        Args:
            mode: 'paper' (default) or 'dhan' (live)
        """
        self.mode = (mode or "paper").lower()
        self.logger = logger
        self.account_equity = 1_000_000  # Simulated capital for paper
        self.positions: Dict[str, Dict[str, Any]] = (
            {}
        )  # symbol -> { quantity, avg_price, raw }
        self.open_orders: Dict[str, Dict[str, Any]] = (
            {}
        )  # client_order_id -> order dict

        # Optional external callback that will receive normalized fill events:
        # callback(fill_event: dict) -> None
        self._fill_callback: Optional[Callable[[Dict[str, Any]], None]] = None

        # Threading pool for simulated fills (paper mode) to avoid blocking
        self._sim_threads: List[threading.Thread] = []

        # Initialize live adapter if requested
        if self.mode == "dhan" and DhanAdapter is not None:
            try:
                self.adapter = DhanAdapter()
                self.logger.info("Live DhanAdapter mode enabled.")
            except Exception as e:
                self.logger.error("Failed to initialize DhanAdapter: %s", e)
                self.adapter = None
        else:
            self.adapter = None
            if self.mode == "dhan":
                self.logger.warning(
                    "DhanAdapter not available; falling back to paper-mode behavior."
                )
            self.logger.info("Paper trading mode enabled.")

    # -------------------------
    # Callback registration
    # -------------------------
    def set_fill_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register a callback to receive fill events.
        ExecutionEngine.on_fill is a good candidate.
        """
        self._fill_callback = callback

    def _emit_fill(self, fill_event: Dict[str, Any]):
        """
        Emit a fill_event via the registered callback, non-blocking.
        """
        if self._fill_callback:
            try:
                # Call in a background thread so adapter does not block
                t = threading.Thread(
                    target=self._safe_call_callback, args=(fill_event,), daemon=True
                )
                t.start()
            except Exception as e:
                self.logger.exception("Failed to start fill callback thread: %s", e)

    def _safe_call_callback(self, fill_event: Dict[str, Any]):
        try:
            self._fill_callback(fill_event)
        except Exception as e:
            self.logger.exception("Fill callback raised: %s", e)

    # -------------------------
    # Account helpers
    # -------------------------
    def get_account_equity(self) -> float:
        if self.mode == "dhan" and self.adapter:
            try:
                bal = self.adapter.get_balance()
                return float(bal.get("availableCash", 0))
            except Exception as e:
                self.logger.error("Failed to fetch Dhan balance: %s", e)
                return 0.0
        return float(self.account_equity)

    # -------------------------
    # Order submission
    # -------------------------
    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float = 0.0,
        *,
        client_order_id: Optional[str] = None,
        order_meta: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Submit an order. Returns an order dict (normalized).
        For paper mode, simulates a fill asynchronously.
        """
        side = (side or "buy").lower()
        client_order_id = client_order_id or f"{symbol}_{int(time.time()*1000)}"
        order_meta = order_meta or {}

        order = {
            "client_order_id": client_order_id,
            "symbol": symbol,
            "side": side,
            "quantity": int(quantity),
            "price": float(price) if price else 0.0,
            "status": "new",
            "meta": order_meta,
            **kwargs,
        }

        # store order
        self.open_orders[client_order_id] = order
        self.logger.debug("Order received: %s", order)

        if self.mode == "paper":
            # simulate fill asynchronously
            t = threading.Thread(
                target=self._simulate_fill_async, args=(order,), daemon=True
            )
            t.start()
            self._sim_threads.append(t)
            return order

        elif self.mode == "dhan":
            return self._submit_live_order(order)

        else:
            raise ValueError(f"Unsupported broker mode: {self.mode}")

    def _simulate_fill_async(self, order: Dict[str, Any]):
        """
        Simulate network/exchange latency and fill the paper order.
        """
        try:
            # fake latency
            time.sleep(random.uniform(0.05, 0.5))

            # determine fill price (small slippage)
            if order.get("price", 0) > 0:
                fill_price = order["price"] * random.uniform(0.997, 1.003)
            else:
                fill_price = random.uniform(90.0, 110.0)

            fill_price = round(float(fill_price), 2)
            order_id = order["client_order_id"]

            # mark as open/filled
            fill_event = {
                "trade_id": order_id,
                "client_order_id": order_id,
                "symbol": order["symbol"],
                "side": order["side"].upper(),
                "filled_qty": order["quantity"],
                "avg_fill_price": fill_price,
                "status": "CLOSED",  # simulated instantaneous fill for simplicity
                "close_reason": None,
                "pnl": 0.0,  # pnl computed by execution engine when closed later
                "order_meta": order.get("meta", {}),
            }

            # Update positions (simple entry/exit)
            self._update_position_after_fill(fill_event)

            # remove from open_orders
            if order_id in self.open_orders:
                self.open_orders.pop(order_id, None)

            # emit to callback
            self._emit_fill(fill_event)

            self.logger.info(
                "[Simulated Fill] %s %s %d @ %s",
                fill_event["side"],
                fill_event["symbol"],
                fill_event["filled_qty"],
                fill_event["avg_fill_price"],
            )
        except Exception as e:
            self.logger.exception("Simulated fill failed: %s", e)

    def _submit_live_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit order to live adapter. This is synchronous; adapter should ideally be async or evented.
        """
        if not self.adapter:
            self.logger.error("Live adapter missing; cannot send order.")
            order["status"] = "error"
            order["error"] = "adapter_missing"
            return order

        try:
            res = self.adapter.place_order(
                order["symbol"],
                order["side"],
                order["quantity"],
                price=order.get("price"),
            )
            # adapter-specific mapping; keep normalized keys
            order["status"] = res.get("status", "open")
            order["exchange_order_id"] = res.get("order_id")
            self.logger.info("Live order submitted: %s", order["exchange_order_id"])
            return order
        except Exception as e:
            self.logger.exception("Live order submission failed: %s", e)
            order["status"] = "error"
            order["error"] = str(e)
            return order

    # -------------------------
    # Position bookkeeping
    # -------------------------
    def _update_position_after_fill(self, fill_event: Dict[str, Any]):
        """
        Very simple position tracker: sum FIFO-less quantities and update avg_price.
        """
        symbol = fill_event.get("symbol")
        qty = int(fill_event.get("filled_qty", 0))
        price = float(fill_event.get("avg_fill_price", 0.0))
        side = (fill_event.get("side") or "BUY").upper()

        pos = self.positions.get(symbol, {"quantity": 0, "avg_price": 0.0})
        current_qty = int(pos.get("quantity", 0))

        if side == "BUY":
            # new average price
            total_cost = current_qty * pos.get("avg_price", 0.0) + qty * price
            new_qty = current_qty + qty
            new_avg = (total_cost / new_qty) if new_qty else 0.0
            self.positions[symbol] = {
                "quantity": new_qty,
                "avg_price": new_avg,
                "raw": {},
            }
        else:  # SELL
            # reduce position; avg_price unchanged for remaining
            new_qty = max(0, current_qty - qty)
            self.positions[symbol] = {
                "quantity": new_qty,
                "avg_price": pos.get("avg_price", 0.0),
                "raw": {},
            }

    # -------------------------
    # SL / TP Checking
    # -------------------------
    def check_stop_loss_take_profit(
        self, order: Dict[str, Any], current_price: float, config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if an order's SL or TP would be hit given the current_price and config.
        Returns:
            {"hit": "stop_loss" | "take_profit"} or None if neither hit.
        Config keys:
            stop_loss_pct: fraction e.g. 0.02
            take_profit_pct: fraction e.g. 0.03
        """
        try:
            entry_price = (
                order.get("execution_price")
                or order.get("entry_price")
                or order.get("price")
            )
            if entry_price is None or entry_price == 0 or current_price is None:
                return None

            side = (order.get("side") or "buy").lower()
            sl_pct = float(config.get("stop_loss_pct", 0.02))
            tp_pct = float(config.get("take_profit_pct", 0.03))

            if side == "buy":
                if current_price <= entry_price * (1 - sl_pct):
                    return {"hit": "stop_loss"}
                if current_price >= entry_price * (1 + tp_pct):
                    return {"hit": "take_profit"}
            else:  # sell
                if current_price >= entry_price * (1 + sl_pct):
                    return {"hit": "stop_loss"}
                if current_price <= entry_price * (1 - tp_pct):
                    return {"hit": "take_profit"}
        except Exception as e:
            self.logger.exception("SL/TP check error: %s", e)
        return None

    # -------------------------
    # Utility APIs
    # -------------------------
    def cancel_all_orders(self) -> bool:
        if self.mode == "dhan" and self.adapter:
            try:
                return self.adapter.cancel_all_orders()
            except Exception as e:
                self.logger.error("Cancel all orders failed: %s", e)
                return False
        else:
            # Clear simulated open orders
            self.open_orders.clear()
            self.logger.info("All simulated orders cleared (paper mode).")
            return True

    def kill_switch(self) -> str:
        if self.mode == "dhan" and self.adapter:
            try:
                return self.adapter.kill_switch()
            except Exception as e:
                self.logger.error("Kill switch failed: %s", e)
                return "Kill switch error"
        else:
            self.logger.warning(
                "Kill switch triggered in paper mode — no action taken."
            )
            return "Paper mode — kill switch bypassed."

    def get_open_position(self, symbol: str) -> Dict[str, Any]:
        """
        Returns dict with quantity, avg_price, raw
        """
        return self.positions.get(symbol, {"quantity": 0, "avg_price": 0.0, "raw": {}})

    # -------------------------
    # Helpers for testing / shutdown
    # -------------------------
    def wait_for_all_simulated_fills(self, timeout: float = 5.0):
        """
        Wait for all simulation threads to finish or until timeout (seconds).
        """
        start = time.time()
        for t in list(self._sim_threads):
            remaining = max(0.0, timeout - (time.time() - start))
            if remaining <= 0:
                break
            t.join(timeout=remaining)
        # clear finished threads
        self._sim_threads = [t for t in self._sim_threads if t.is_alive()]
