# modules/backtester/slippage.py
from dataclasses import dataclass
from typing import Tuple
import math

@dataclass
class Order:
    order_id: str
    symbol: str
    side: str  # 'BUY' or 'SELL'
    qty: float
    price: float  # limit or market reference price
    meta: dict = None

class SlippageModel:
    """
    Abstract slippage model. Implementations must provide fill(order, bar).
    bar is a dict-like with at least: 'open','high','low','close','volume'
    """
    def fill(self, order: Order, bar) -> Tuple[float, float, str]:
        raise NotImplementedError


class VWAPSliceSlippage(SlippageModel):
    """
    Deterministic VWAP-style volumetric slippage:
      - participation_rate: fraction of bar volume we attempt to capture (0-1)
      - max_slice_fraction: max fraction of bar volume executed in a single slice
      - impact_per_unit: price impact per unit executed (signed by side)
    Behavior:
      - target_fill = min(order.qty, participation_rate * bar_volume)
      - slice_size = min(max_slice_fraction * bar_volume, target_fill)
      - number_of_slices = ceil(target_fill / slice_size)
      - avg_price = weighted average: we model each slice hitting at bar close + slice_index*impact
    """
    def __init__(self, participation_rate: float = 0.1, max_slice_fraction: float = 0.25, impact_per_unit: float = 0.0):
        assert 0 <= participation_rate <= 1.0
        assert 0 < max_slice_fraction <= 1.0
        self.participation_rate = participation_rate
        self.max_slice_fraction = max_slice_fraction
        self.impact_per_unit = impact_per_unit

    def fill(self, order: Order, bar):
        vol = float(bar.get("volume", 0.0) or 0.0)
        if vol <= 0 or order.qty <= 0:
            return 0.0, float(order.price), "open"

        target_fill = min(order.qty, self.participation_rate * vol)
        if target_fill <= 0:
            return 0.0, float(order.price), "open"

        slice_size = min(self.max_slice_fraction * vol, target_fill)
        n_slices = int(math.ceil(target_fill / slice_size))
        filled = 0.0
        cum_price = 0.0

        # Determine side multiplier: BUY pushes price up, SELL pushes down
        side_mul = 1.0 if order.side.upper() == "BUY" else -1.0

        for i in range(n_slices):
            this_slice = slice_size if (filled + slice_size) <= target_fill else (target_fill - filled)
            # Simulate price impact increasing with each slice index (simple linear)
            impact = (i + 1) * self.impact_per_unit * side_mul
            slice_price = float(bar.get("close", order.price)) + impact
            cum_price += this_slice * slice_price
            filled += this_slice

        avg_price = (cum_price / filled) if filled > 0 else float(order.price)
        status = "filled" if abs(filled - order.qty) < 1e-9 or filled >= order.qty else "partial"
        return float(filled), float(avg_price), status
