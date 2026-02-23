# backtest/position_manager.py
from typing import Dict, Any


class SimplePositionManager:
    """
    Track positions and (optionally) P&L from fills. Expects provider.fill dicts like PaperProvider.
    """

    def __init__(self, provider=None):
        self.positions = {}
        self.provider = provider

    def record_fill(self, order: Dict[str, Any], fill: Dict[str, Any]):
        symbol = order.get("symbol")
        qty = int(order.get("quantity") or order.get("qty") or 0)
        side = order.get("side")
        if side == "buy":
            self.positions[symbol] = self.positions.get(symbol, 0) + qty
        elif side == "sell":
            current = self.positions.get(symbol, 0)
            self.positions[symbol] = max(0, current - qty)
