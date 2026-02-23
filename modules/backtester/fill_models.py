"""
Volumetric slippage + partial-fill simulation utilities.

Purpose:
- Provide deterministic, testable fill-models for the backtester.
- Keep API small: bars_to_ticks(), VolumetricImpact, simulate_partial_fill().

Expectations:
- Input bars are pandas DataFrame with index timestamps and columns:
  ['open','high','low','close','volume'] (volume optional).
- All functions are pure (no global state).
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

import numpy as np
import pandas as pd


@dataclass
class Fill:
    timestamp: pd.Timestamp
    qty: float
    price: float


@dataclass
class FillResult:
    filled_quantity: float
    avg_price: float
    fills: List[Fill]


class VolumetricImpact:
    """
    Market-impact style volumetric slippage.

    execution_price = touch_price * (1 + direction * (base_pct + sensitivity * (consumed_fraction ** exponent)))

    - consumed_fraction = executed_qty / tick_liquidity (capped to 1.0)
    - direction: + for buys (price rises), - for sells (price falls)
    """

    def __init__(
        self,
        base_pct: float = 0.0005,
        sensitivity: float = 0.6,
        exponent: float = 0.5,
        min_tick_liquidity: float = 1.0,
    ):
        self.base_pct = float(base_pct)
        self.sensitivity = float(sensitivity)
        self.exponent = float(exponent)
        self.min_tick_liquidity = float(max(1.0, min_tick_liquidity))

    def apply(
        self,
        side: str,
        touch_price: float,
        executed_qty: float,
        tick_liquidity: Optional[float],
    ) -> float:
        tick_liq = float(tick_liquidity) if tick_liquidity and tick_liquidity > 0 else self.min_tick_liquidity
        consumed_frac = min(1.0, max(0.0, float(executed_qty) / tick_liq))
        impact = self.sensitivity * (consumed_frac ** self.exponent)
        direction = 1.0 if str(side).upper().startswith("B") else -1.0
        slippage_pct = self.base_pct + impact
        return float(touch_price) * (1.0 + direction * slippage_pct)


def bars_to_ticks(bars: pd.DataFrame, default_liquidity: float = 100.0) -> pd.DataFrame:
    """
    Convert OHLCV bars -> lightweight tick-like rows used by the fill simulator.

    Result columns:
      ['timestamp','bid','ask','bid_size','ask_size','mid','volume']

    Heuristic:
      - bid/ask are derived from close +/- 25% of range
      - bid_size/ask_size are proportional to volume (or default_liquidity)
    """
    if bars is None or bars.empty:
        return pd.DataFrame(columns=["timestamp", "bid", "ask", "bid_size", "ask_size", "mid", "volume"]).set_index("timestamp")

    df = pd.DataFrame(index=bars.index)
    rng = (bars["high"] - bars["low"]).fillna(0.0)
    df["bid"] = bars["close"] - rng * 0.25
    df["ask"] = bars["close"] + rng * 0.25
    vol = bars.get("volume", pd.Series(default_liquidity, index=bars.index)).fillna(default_liquidity)
    # scale size so that average bar volume -> default_liquidity
    mean_vol = float(max(1.0, vol.mean()))
    df["bid_size"] = (vol / mean_vol) * default_liquidity
    df["ask_size"] = df["bid_size"]
    df["mid"] = (df["bid"] + df["ask"]) / 2.0
    df["volume"] = vol
    df = df.reset_index().rename(columns={"index": "timestamp"}).set_index("timestamp")
    return df


def simulate_partial_fill(
    side: str,
    order_qty: float,
    order_price: float,
    ticks: pd.DataFrame,
    impact_model: Optional[VolumetricImpact] = None,
    max_aggressive_fraction: float = 1.0,
    min_fill_size: float = 1.0,
) -> FillResult:
    """
    Simulate filling `order_qty` against tick rows.

    Args:
      side: 'BUY' or 'SELL'
      order_qty: positive
      order_price: price benchmark (limit price or market benchmark)
      ticks: DataFrame produced by bars_to_ticks indexed by timestamp.
      impact_model: VolumetricImpact instance, default provided if None.
      max_aggressive_fraction: fraction of tick-side size we may consume in a single tick (0..1)
      min_fill_size: minimal atomic fill qty; ticks where available < min_fill_size are skipped.

    Returns:
      FillResult with fills chronological order.
    """
    if order_qty <= 0:
        return FillResult(0.0, 0.0, [])

    if impact_model is None:
        impact_model = VolumetricImpact()

    remaining = float(order_qty)
    fills: List[Fill] = []
    total_cost = 0.0
    filled = 0.0

    # iterate ticks in order
    for ts, r in ticks.iterrows():
        if remaining <= 0:
            break

        if str(side).upper().startswith("B"):
            side_size = float(r.get("ask_size", 0.0))
            touch_price = float(r.get("ask", order_price))
        else:
            side_size = float(r.get("bid_size", 0.0))
            touch_price = float(r.get("bid", order_price))

        # available at this tick
        available = max(0.0, side_size * float(max_aggressive_fraction))
        if available <= 0:
            continue

        to_take = min(remaining, available)
        if to_take < min_fill_size:
            continue

        # quantize to integer multiples of min_fill_size (round down)
        to_take = float(math.floor(to_take / min_fill_size) * min_fill_size)
        if to_take <= 0:
            continue

        exec_price = impact_model.apply(side, touch_price, to_take, tick_liquidity=float(r.get("volume", side_size)))
        fills.append(Fill(timestamp=pd.Timestamp(ts), qty=to_take, price=float(exec_price)))
        total_cost += to_take * float(exec_price)
        filled += to_take
        remaining -= to_take

    avg_price = float(total_cost / filled) if filled > 0 else 0.0
    return FillResult(filled_quantity=filled, avg_price=avg_price, fills=fills)
