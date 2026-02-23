# modules/backtester/supercharged_backtester.py
"""
Supercharged backtester (lightweight) integrated with FillModelAdapter.

- Strategies return module.backtester.volumetric_slippage.Order objects (or compatible)
- Backtester tracks remaining_qty across bars using order.meta['remaining_qty']
- For each bar, backtester calls adapter.fill(order, bar, remaining_qty) and records fills
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import pandas as pd

from modules.backtester.volumetric_slippage import Order
from modules.backtester.fill_model_adapter import FillModelAdapter

@dataclass
class FillRecord:
    order_id: str
    symbol: str
    side: str
    qty: float
    price: float
    status: str
    bar_time: Any

@dataclass
class BacktestResult:
    trades: List[FillRecord] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

class SuperchargedBacktester:
    def __init__(self, bars: pd.DataFrame, strategies: List[Any], fill_adapter: FillModelAdapter = None):
        """
        bars: pd.DataFrame indexed by datetime with columns open,high,low,close,volume
        strategies: list of strategy objects with method on_bar(bar) -> List[Order]
        fill_adapter: FillModelAdapter instance (if None, created with defaults)
        """
        self.bars = bars.copy()
        self.strategies = strategies
        self.fill_adapter = fill_adapter or FillModelAdapter()
        self.trades: List[FillRecord] = []

    def run(self) -> BacktestResult:
        for ts, row in self.bars.iterrows():
            bar = row.to_dict()
            bar["time"] = ts
            for strat in self.strategies:
                orders = strat.on_bar(bar) or []
                for o in orders:
                    if not isinstance(o, Order):
                        raise TypeError("Strategy returned non-Order: %r" % (o,))
                    # initialize meta and remaining tracking
                    if o.meta is None:
                        o.meta = {}
                    remaining = float(o.meta.get("remaining_qty", o.qty))
                    if remaining <= 0:
                        # nothing to do for this order
                        continue

                    filled_qty, avg_price, status = self.fill_adapter.fill(o, bar, remaining_qty=remaining)

                    # Record the fill (only if something was filled)
                    if filled_qty and filled_qty > 0:
                        rec = FillRecord(
                            order_id=o.order_id,
                            symbol=o.symbol,
                            side=o.side,
                            qty=filled_qty,
                            price=avg_price,
                            status=status,
                            bar_time=ts
                        )
                        self.trades.append(rec)

                    # update remaining in-place so subsequent bars know remaining
                    new_remaining = max(0.0, remaining - filled_qty)
                    o.meta["remaining_qty"] = new_remaining

        # summarize: total filled qty and notional per symbol
        summary = {}
        for t in self.trades:
            s = summary.setdefault(t.symbol, {"filled_qty": 0.0, "notional": 0.0})
            # BUY increments filled_qty, SELL decrements (but that depends on your convention)
            s["filled_qty"] += t.qty if t.side.upper() == "BUY" else -t.qty
            s["notional"] += t.qty * t.price if t.side.upper() == "BUY" else -t.qty * t.price

        return BacktestResult(trades=self.trades, summary=summary)
