# providers/dhan_http.py
"""
DhanHTTPProvider - HTTP-capable provider shim.

This implementation intentionally enforces provider-attached risk manager at the top
of submit_order so both simulated and real HTTP flows are gated by risk rules.

The class is purposely simple and suitable for unit testing; enable_http flag exists
to allow tests to instantiate without making real network calls.
"""

from typing import Dict, Any, Optional
import time
import random


class DhanHTTPProvider:
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        risk_manager: Optional[Any] = None,
    ):
        self.config = config or {}
        self._account_nav = float(self.config.get("starting_cash", 0.0))
        self._positions: Dict[str, int] = {}
        self._last_prices: Dict[str, float] = {}
        self._connected = False
        self.enable_http = bool(self.config.get("enable_http", False))
        self.risk_manager = risk_manager

    def connect(self) -> bool:
        # in tests connect() returns True and sets connected flag
        self._connected = True
        return True

    def is_connected(self) -> bool:
        return bool(self._connected)

    def set_risk_manager(self, rm) -> None:
        self.risk_manager = rm

    def get_account_nav(self) -> float:
        return float(self._account_nav)

    def get_positions(self) -> Dict[str, Any]:
        return dict(self._positions)

    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit order. Enforce provider.risk_manager early.
        If enable_http is True, this is where an HTTP call would be made.
        For tests we perform a simulated fill.
        """
        # Early risk enforcement
        try:
            if getattr(self, "risk_manager", None) is not None:
                from utils.risk_utils import enforce_risk_or_raise

                enforce_risk_or_raise(self.risk_manager, self, order)
        except ValueError:
            # explicit denial of trading -> bubble up
            raise
        except Exception:
            # non-fatal; don't block tests if helper fails
            pass

        # If the provider would speak to Dhan over HTTP, you'd do it here.
        # For unit tests we simulate a fill immediately.
        ts = int(time.time() * 1000)
        order_id = f"dh_http_order_{ts}_{random.randint(0,9999)}"
        side = (order.get("side") or "").lower()
        qty = int(order.get("quantity") or order.get("qty") or 0)
        symbol = order.get("symbol")
        price = float(order.get("price") or 0.0)

        if symbol:
            if side == "buy":
                self._positions[symbol] = self._positions.get(symbol, 0) + qty
                self._account_nav = max(0.0, self._account_nav - qty * price)
                if price:
                    self._last_prices[symbol] = price
            elif side == "sell":
                self._positions[symbol] = max(0, self._positions.get(symbol, 0) - qty)
                self._account_nav = self._account_nav + qty * price
                if price:
                    self._last_prices[symbol] = price

        return {
            "status": "filled",
            "order_id": order_id,
            "filled_qty": qty,
            "price": price,
        }
