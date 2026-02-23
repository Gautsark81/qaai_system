# modules/backtester/volumetric_slippage.py
"""
Volumetric slippage model with partial-fill semantics.

Model idea (deterministic VWAP-style slice):
- For each bar, attempt participation_rate * bar_volume, subject to max_slice_fraction per slice.
- Target per-bar capture = min(remaining_qty, participation_rate * bar_volume)
- We slice that target into slices (max per slice = max_slice_fraction * bar_volume)
- Each slice executes at bar_close +/- linear impact (impact_per_unit * cumulative_executed)
- Returns (filled_qty_this_call, avg_price, status) where status in {'filled','partial','open'}
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple
import math

@dataclass
class Order:
    order_id: str
    symbol: str
    side: str  # 'BUY' or 'SELL'
    qty: float  # original requested qty
    price: float  # reference price (limit or market reference)
    meta: Dict[str, Any] = None

class VolumetricSlippage:
    def __init__(self, participation_rate: float = 0.1, max_slice_fraction: float = 0.25, impact_per_unit: float = 0.0001):
        """
        participation_rate: fraction of bar volume we try to capture (0-1)
        max_slice_fraction: max fraction of bar volume in any single slice (0-1)
        impact_per_unit: price impact per unit executed (absolute price units); a small number
        """
        assert 0.0 <= participation_rate <= 1.0
        assert 0.0 < max_slice_fraction <= 1.0
        self.participation_rate = participation_rate
        self.max_slice_fraction = max_slice_fraction
        self.impact_per_unit = float(impact_per_unit)

    def fill(self, order: Order, bar: Dict[str, Any], remaining_qty: float = None) -> Tuple[float, float, str]:
        """
        Attempt to fill part or all of 'remaining_qty' using this bar's volume.

        bar: dict with keys: 'open','high','low','close','volume' (volume must be numeric >=0)
        remaining_qty: how much quantity remains to be filled for this order (float).
                       If None, uses order.qty.

        Returns: (filled_qty_this_call, avg_price, status)
        - status 'filled' if after this call remaining becomes 0 (within 1e-9)
        - 'partial' if some quantity was filled but remaining > 0
        - 'open' if nothing filled
        """
        if remaining_qty is None:
            remaining_qty = float(order.qty)

        vol = float(bar.get("volume", 0.0) or 0.0)
        if vol <= 0 or remaining_qty <= 0:
            return 0.0, float(order.price), "open"

        # target we try to capture from this bar
        per_bar_capacity = self.participation_rate * vol
        target_fill = min(remaining_qty, per_bar_capacity)
        if target_fill <= 0:
            return 0.0, float(order.price), "open"

        # slice size limited by max_slice_fraction * bar_volume
        slice_capacity = max(1e-9, self.max_slice_fraction * vol)
        n_slices = int(math.ceil(target_fill / slice_capacity))
        filled = 0.0
        cum_price = 0.0

        # sign: buy pushes price up, sell pushes down
        side_mul = 1.0 if (order.side or "").upper() == "BUY" else -1.0

        # Model linear increasing impact across slices (simple and deterministic)
        for i in range(n_slices):
            this_slice = slice_capacity if (filled + slice_capacity) <= target_fill else (target_fill - filled)
            # price baseline uses bar close if present else order.price
            base_price = float(bar.get("close", order.price))
            # impact increases linearly with cumulative executed units
            impact = (filled + this_slice) * self.impact_per_unit * side_mul
            slice_price = base_price + impact
            cum_price += this_slice * slice_price
            filled += this_slice

        avg_price = (cum_price / filled) if filled > 0 else float(order.price)

        # Determine status relative to original order qty
        new_remaining = remaining_qty - filled
        status = "filled" if new_remaining <= 1e-9 else "partial"
        return float(filled), float(avg_price), status
