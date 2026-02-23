# backtest/pnl.py
from typing import Dict, Any
from collections import defaultdict


class PnLCalculator:
    """
    Very small P&L calculator that tracks positions (qty, avg_cost),
    computes realized P&L on sells, and provides unrealized by last price.
    """

    def __init__(self):
        self.positions = {}  # symbol -> {"qty": int, "avg_cost": float}
        self.realized = defaultdict(float)

    def record_fill(self, fill: Dict[str, Any], order: Dict[str, Any]):
        symbol = order.get("symbol")
        qty = int(order.get("quantity") or 0)
        side = order.get("side")
        price = float(order.get("price") or fill.get("price") or 0.0)
        if symbol not in self.positions:
            self.positions[symbol] = {"qty": 0, "avg_cost": 0.0}

        pos = self.positions[symbol]
        if side == "buy":
            total_cost = pos["avg_cost"] * pos["qty"] + price * qty
            pos["qty"] += qty
            pos["avg_cost"] = total_cost / pos["qty"] if pos["qty"] else 0.0
        elif side == "sell":
            # realize P&L based on avg_cost
            realized = (price - pos["avg_cost"]) * qty
            self.realized[symbol] += realized
            pos["qty"] = max(0, pos["qty"] - qty)
            if pos["qty"] == 0:
                pos["avg_cost"] = 0.0

    def unrealized(self, market_prices: Dict[str, float]) -> Dict[str, float]:
        out = {}
        for sym, pos in self.positions.items():
            last = float(market_prices.get(sym, pos.get("avg_cost") or 0.0))
            out[sym] = (last - pos.get("avg_cost", 0.0)) * pos.get("qty", 0)
        return out

    def summary(self, market_prices: Dict[str, float]) -> Dict[str, Any]:
        unreal = self.unrealized(market_prices)
        total_unreal = sum(unreal.values())
        total_real = sum(self.realized.values())
        return {
            "realized": total_real,
            "unrealized": total_unreal,
            "positions": dict(self.positions),
        }
