# strategies/mavg_cross.py
from typing import Dict, Any, Optional
from .base import StrategyBase


class MovingAverageCrossStrategy(StrategyBase):
    """
    Simple EMA crossover:
      - buy qty from config when short_ema crosses above long_ema
      - sell full position when short_ema crosses below long_ema
    Expects features like "ema_<period>" produced by build_features_from_ohlcv.
    """

    def __init__(self, config=None):
        super().__init__(config=config)
        self.position = 0

    def on_start(self, context):
        super().on_start(context)
        self.symbol = context.get("symbol")  # optional context hint
        self.position = 0

    def on_bar(
        self, symbol: str, bar: Dict[str, Any], features: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # determine short / long ema names from config or defaults
        short_p = self.config.get("short_period", 8)
        long_p = self.config.get("long_period", 21)
        qty = int(self.config.get("order_qty", 1))

        short_key = f"ema_{short_p}"
        long_key = f"ema_{long_p}"
        short_series = features.get(short_key) if features else None
        long_series = features.get(long_key) if features else None
        if not short_series or not long_series:
            return None

        short_val = short_series[-1] if len(short_series) else None
        long_val = long_series[-1] if len(long_series) else None

        # Not enough data yet
        if short_val is None or long_val is None:
            return None

        # Buy signal
        if short_val > long_val and self.position <= 0:
            order = {
                "symbol": symbol,
                "side": "buy",
                "quantity": qty,
                "price": float(bar.get("close") or bar.get("price") or 0),
            }
            return order

        # Sell / close signal
        if short_val < long_val and self.position > 0:
            order = {
                "symbol": symbol,
                "side": "sell",
                "quantity": self.position,
                "price": float(bar.get("close") or bar.get("price") or 0),
            }
            return order

        return None

    def on_order_filled(self, order, fill):
        # naive fill handling: update position count
        side = order.get("side")
        qty = int(order.get("quantity") or order.get("qty") or 0)
        if side == "buy":
            self.position += qty
        elif side == "sell":
            self.position = max(0, self.position - qty)
