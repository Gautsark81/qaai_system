# qaai_system/execution/paper_provider.py
from typing import Dict, Any, List
from .base import ExecutionProvider
from .position_manager import PositionManager
import time


class PaperExecutionProvider(ExecutionProvider):
    """
    Simulated execution provider for paper trading.
    Integrates a PositionManager to compute accurate realized/unrealized PnL.
    Now includes fill queue to support orchestrator polling.
    """

    def __init__(self, pm_method: str = "fifo"):
        self._orders: Dict[str, Dict[str, Any]] = {}
        self._positions: Dict[str, Any] = {}
        self._counter = 0
        self._account_nav = 100000.0
        self._fills: List[Dict[str, Any]] = []

        self.pm = PositionManager(method=pm_method)

    def _next_id(self) -> str:
        self._counter += 1
        return f"paper_{int(time.time() * 1000)}_{self._counter}"

    def submit_order(self, order: Dict[str, Any]) -> str:
        oid = self._next_id()
        symbol = order.get("symbol")
        qty = int(order.get("qty") or order.get("quantity") or 0)
        side = str(order.get("side", "buy")).lower()

        if side not in {"buy", "sell"}:
            if qty < 0:
                side = "sell"
                qty = abs(qty)
            else:
                side = "buy"

        mid_price = (
            order.get("price") or order.get("mid_price") or order.get("limit_price")
        )
        if mid_price is None:
            mid_price = float(self._positions.get(f"__last_price__:{symbol}", 100.0))

        slippage_bps = float(order.get("slippage_bps", 0.0))
        fill_price = float(mid_price) * (1.0 + slippage_bps / 10000.0)

        filled_qty = qty
        realized = self.pm.on_fill(symbol, side, filled_qty, fill_price)

        self._orders[oid] = {
            "order_id": oid,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "filled_qty": filled_qty,
            "avg_price": float(fill_price),
            "status": "FILLED",
            "created_at": time.time(),
            "slippage_bps": slippage_bps,
            "realized_pnl": float(realized),
        }

        # record for orchestrator
        self._fills.append(
            {
                "order_id": oid,
                "symbol": symbol,
                "side": side,
                "qty": filled_qty,
                "price": fill_price,
                "timestamp": time.time(),
            }
        )

        self._positions[symbol] = int(self.pm.get_position(symbol)["qty"])
        self._positions[f"__last_price__:{symbol}"] = float(mid_price)

        return oid

    def fetch_fills(self) -> List[Dict[str, Any]]:
        """
        Return simulated fills (used by orchestrator.poll)
        """
        fills = self._fills
        self._fills = []
        return fills

    def cancel_order(self, order_id: str) -> bool:
        if order_id in self._orders and self._orders[order_id]["status"] != "FILLED":
            self._orders[order_id]["status"] = "CANCELLED"
            return True
        return False

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        return self._orders.get(
            order_id,
            {
                "order_id": order_id,
                "status": "UNKNOWN",
                "filled_qty": 0,
                "avg_price": 0.0,
            },
        )

    def get_positions(self) -> Dict[str, Any]:
        return {
            k: v
            for k, v in self._positions.items()
            if not k.startswith("__last_price__")
        }

    def get_open_orders(self) -> List[str]:
        return [
            oid
            for oid, md in self._orders.items()
            if md.get("status") not in ("FILLED", "CANCELLED")
        ]

    def get_last_price(self, symbol: str):
        return self._positions.get(f"__last_price__:{symbol}")

    def get_account(self) -> Dict[str, Any]:
        return {"nav": float(self._account_nav)}
