"""
Backtester core — compatibility layer plus improved core engine.

Compatibility additions:
- Backtester(..., slippage=..., fill_hook=...) accepted by older tests
- Backtester.place_order(...) implemented (returns order_id)
- Backtester.get_order(order_id) implemented
- Backtester.run_to_end() implemented to process pending orders
- Backtester.summary() implemented (brief order summary)
- FixedTickSlippage supports tick_size and ticks kwarg names
- PercentSlippage provided

Modern components retained:
- BacktesterCore, Order, FillEvent, VolumetricImpact, simulate_partial_fill integration
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Callable
import logging
import math
import datetime as dt
import uuid

import pandas as pd
import numpy as np

from modules.backtester.fill_models import VolumetricImpact, bars_to_ticks, simulate_partial_fill, FillResult, Fill

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# ---------------------------
# Backward-compatible slippage models
# ---------------------------
class FixedTickSlippage:
    """
    Simple slippage model: moves price by a fixed number of ticks.

    Supports constructor signatures:
      FixedTickSlippage(tick_size=0.01, ticks=1)
      FixedTickSlippage(ticks=2)
      FixedTickSlippage(tick_size=0.1)
    """

    def __init__(self, tick_size: float = 0.01, ticks: float = 1.0, **kwargs):
        # accept kwargs for compatibility with different test callsites
        # e.g., tests may pass tick_size, ticks or other alias; we ignore unknown keys
        self.tick_size = float(tick_size)
        self.ticks = float(ticks)

    def apply(self, side: str, touch_price: float, *_, **__):
        direction = 1.0 if str(side).upper().startswith("B") else -1.0
        return float(touch_price) + direction * (self.tick_size * self.ticks)


class PercentSlippage:
    """
    Slippage as percentage move from touch.
    Example: pct=0.001 => 0.1% slippage directionally applied.
    """

    def __init__(self, pct: float = 0.001):
        self.pct = float(pct)

    def apply(self, side: str, touch_price: float, *_, **__):
        direction = 1.0 if str(side).upper().startswith("B") else -1.0
        return float(touch_price) * (1.0 + direction * self.pct)


# ---------------------------
# Core improved classes (retain previous functionality)
# ---------------------------

@dataclass
class Order:
    order_id: str
    symbol: str
    side: str  # 'BUY' / 'SELL'
    quantity: float
    price: float  # limit price or benchmark
    created_at: Optional[dt.datetime] = None
    filled_qty: float = 0.0
    avg_fill_price: Optional[float] = None
    status: str = "new"
    meta: Dict[str, Any] = field(default_factory=dict)

    def remaining(self) -> float:
        return max(0.0, float(self.quantity) - float(self.filled_qty))

    def apply_fill(self, qty: float, price: float) -> None:
        if qty <= 0:
            return
        prev_qty = float(self.filled_qty)
        prev_avg = float(self.avg_fill_price or 0.0)
        new_qty = prev_qty + float(qty)
        self.avg_fill_price = ((prev_avg * prev_qty) + (float(price) * float(qty))) / new_qty
        self.filled_qty = new_qty
        if math.isclose(self.filled_qty, self.quantity, rel_tol=1e-6) or self.filled_qty >= self.quantity:
            self.status = "filled"
        else:
            # keep 'partially_filled' for internal clarity; summary() will expose friendly counts
            self.status = "partially_filled"


@dataclass
class FillEvent:
    order_id: str
    symbol: str
    side: str
    fill_qty: float
    fill_price: float
    ts: pd.Timestamp
    info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side,
            "fill_qty": float(self.fill_qty),
            "fill_price": float(self.fill_price),
            "ts": pd.Timestamp(self.ts).isoformat(),
        }
        d.update({"info": self.info})
        return d


class MLInferFillAdapter:
    """
    Safe adapter to optionally use an ML fill predictor.

    If no model / function is available, uses a deterministic heuristic fallback.
    """

    def __init__(self, model: Optional[Any] = None, infer_fn: Optional[Callable] = None):
        self._model = model
        self._infer_fn = infer_fn

    def predict_fill(self, symbol: str, price: float, remaining_qty: float, side: str, ts: Optional[pd.Timestamp] = None) -> float:
        # prefer explicit infer_fn if supplied
        try:
            if callable(self._infer_fn):
                p = self._infer_fn(symbol=symbol, price=price, qty=remaining_qty, side=side, ts=ts)
                return float(max(0.0, min(1.0, float(p))))
        except Exception:
            logger.exception("infer_fn failed; falling back to model/heuristic")

        # model object attempts
        try:
            if self._model is not None:
                if hasattr(self._model, "predict_proba"):
                    p = self._model.predict_proba([[remaining_qty, price, 1 if side.upper().startswith("B") else 0]])[0][1]
                    return float(max(0.0, min(1.0, float(p))))
                if hasattr(self._model, "predict"):
                    p = self._model.predict([[remaining_qty, price, 1 if side.upper().startswith("B") else 0]])
                    if isinstance(p, (list, tuple, np.ndarray)):
                        p = p[0]
                    return float(max(0.0, min(1.0, float(p))))
        except Exception:
            logger.exception("model predict failed; falling back to heuristic")

        # deterministic heuristic fallback
        q = float(remaining_qty)
        if q <= 1:
            return 0.95
        if q <= 5:
            return 0.85
        if q <= 20:
            return 0.6
        if q <= 100:
            return 0.35
        return 0.12


class BacktesterCore:
    """
    Main backtester core.
    """

    def __init__(
        self,
        fill_adapter: Optional[MLInferFillAdapter] = None,
        impact_model: Optional[VolumetricImpact] = None,
        liquidity_factor: float = 0.6,
        min_fill_size: float = 1.0,
    ):
        self.fill_adapter = fill_adapter if fill_adapter is not None else MLInferFillAdapter()
        self.impact_model = impact_model if impact_model is not None else VolumetricImpact()
        self.liquidity_factor = float(liquidity_factor)
        self.min_fill_size = float(min_fill_size)

    def simulate_order(self, order: Order, ohlcv: pd.DataFrame, max_aggressive_pct: float = 1.0) -> List[FillEvent]:
        """
        Simulate `order` against OHLCV DataFrame `ohlcv`.
        """
        if ohlcv is None or ohlcv.empty:
            logger.warning("simulate_order: empty market data for %s", order.symbol)
            return []

        ticks = bars_to_ticks(ohlcv)
        fills_out: List[FillEvent] = []

        for ts, row in ticks.sort_index().iterrows():
            if order.remaining() <= 0:
                break

            tick_vol = float(row.get("volume", 0.0) or 0.0)
            side_size = float(row.get("ask_size" if order.side.upper().startswith("B") else "bid_size", 0.0))
            try:
                p_fill = float(self.fill_adapter.predict_fill(order.symbol, order.price, order.remaining(), order.side, ts))
            except Exception:
                logger.exception("fill_adapter failed; defaulting p_fill=0.0")
                p_fill = 0.0

            available_by_volume = p_fill * tick_vol * self.liquidity_factor
            available_by_book = side_size * float(max_aggressive_pct)
            available = max(0.0, min(available_by_volume, available_by_book, order.remaining()))

            # enforce min_fill_size
            if available < self.min_fill_size:
                continue

            to_fill = float(math.floor(available / self.min_fill_size) * self.min_fill_size)
            if to_fill <= 0:
                continue

            exec_price = self.impact_model.apply(order.side, order.price, to_fill, tick_liquidity=tick_vol)
            order.apply_fill(to_fill, exec_price)

            evt = FillEvent(
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                fill_qty=to_fill,
                fill_price=exec_price,
                ts=pd.Timestamp(ts),
                info={"tick_volume": tick_vol, "p_fill": p_fill, "liquidity_used": to_fill / (tick_vol if tick_vol else 1.0)},
            )
            fills_out.append(evt)

        return fills_out

    def run_backtest(self, orders: List[Order], price_map: Dict[str, pd.DataFrame]) -> Dict[str, List[FillEvent]]:
        out = {}
        for o in orders:
            df = price_map.get(o.symbol)
            if df is None:
                logger.warning("Missing market data for %s; skipping order %s", o.symbol, o.order_id)
                out[o.order_id] = []
                continue
            out[o.order_id] = self.simulate_order(o, df)
        return out


# ---------------------------
# Backward-compatible Backtester wrapper
# ---------------------------
class Backtester:
    """
    Compatibility wrapper for older tests that expect `Backtester`.

    Constructor supports:
      Backtester(price_bars)
      Backtester(price_bars, slippage=PercentSlippage(...), fill_hook=callable_or_object)
    """

    def __init__(self, price_bars: Optional[pd.DataFrame] = None, slippage: Optional[Any] = None, fill_hook: Optional[Any] = None):
        # price_bars may be a dict symbol->df in other contexts; keep simple here
        self.price_bars = price_bars if price_bars is not None else pd.DataFrame()
        self.slippage = slippage  # older tests pass a slippage model here
        self.fill_hook = fill_hook  # optional hook called when fills occur
        # internal core to run more advanced simulations when needed
        self._core = BacktesterCore()
        self._orders: Dict[str, Order] = {}

    def _call_fill_hook(self, order_id: Optional[str], fill: Dict[str, Any]) -> None:
        if self.fill_hook is None:
            return
        try:
            # object with on_fill method
            if hasattr(self.fill_hook, "on_fill") and callable(getattr(self.fill_hook, "on_fill")):
                self.fill_hook.on_fill(order_id, fill)
                return
            # callable directly
            if callable(self.fill_hook):
                self.fill_hook(order_id, fill)
                return
        except Exception:
            logger.exception("fill_hook raised an exception; continuing")

    def place_order(self, symbol: str, side: str, qty: float, price: float, when: Optional[pd.Timestamp] = None, order_type: str = "limit"):
        """
        Place an order (compatibility method expected by tests).

        Returns generated order_id (string). This method executes the order immediately
        against available market data (synchronous backtest execution).
        """
        if qty <= 0:
            raise ValueError("qty must be positive")
        ohlcv = None
        if isinstance(self.price_bars, dict):
            ohlcv = self.price_bars.get(symbol)
        else:
            ohlcv = self.price_bars

        # create order record and store (even if no fills)
        oid = f"o-{uuid.uuid4().hex[:8]}"
        order = Order(order_id=oid, symbol=symbol, side=side, quantity=float(qty), price=float(price), created_at=dt.datetime.utcnow())
        self._orders[oid] = order

        if ohlcv is None or ohlcv.empty:
            # nothing to simulate against; return order id (no fills)
            return oid

        # choose start time
        if when is None:
            try:
                when = ohlcv.index[0]
            except Exception:
                when = ohlcv.index[0] if len(ohlcv.index) > 0 else pd.Timestamp.utcnow()

        # perform simulation + apply fills and call hook
        try:
            self._simulate_and_apply_to_order(order, ohlcv, when)
        except Exception:
            logger.exception("place_order simulation failed; returning order id")

        return oid

    def simulate_order(self, symbol: str, side: str, qty: float, when, order_type: str = 'market', max_aggressive_pct: float = 1.0):
        """
        Backward-compatible simulate_order preserved for earlier tests and callsites.
        This returns a dict with 'filled_quantity','avg_price','fills' similar to older implementations.
        """
        if qty <= 0:
            raise ValueError("qty must be positive")

        ohlcv = None
        if isinstance(self.price_bars, dict):
            ohlcv = self.price_bars.get(symbol)
        else:
            ohlcv = self.price_bars

        if ohlcv is None or ohlcv.empty:
            return {"filled_quantity": 0.0, "avg_price": 0.0, "fills": []}

        try:
            start_loc = ohlcv.index.get_loc(when)
        except Exception:
            start_loc = ohlcv.index.searchsorted(when)

        ticks = bars_to_ticks(ohlcv.iloc[start_loc:])

        if self.slippage is not None:
            remaining = float(qty)
            fills = []
            total_cost = 0.0
            filled = 0.0
            for ts, row in ticks.sort_index().iterrows():
                if remaining <= 0:
                    break
                if str(side).upper().startswith("B"):
                    side_size = float(row.get("ask_size", 0.0))
                    touch_price = float(row.get("ask", float(ohlcv["close"].iloc[start_loc] if start_loc < len(ohlcv) else ohlcv["close"].iloc[0])))
                else:
                    side_size = float(row.get("bid_size", 0.0))
                    touch_price = float(row.get("bid", float(ohlcv["close"].iloc[start_loc] if start_loc < len(ohlcv) else ohlcv["close"].iloc[0])))

                available = min(remaining, side_size * float(max_aggressive_pct))
                if available <= 0:
                    continue

                take = float(math.floor(available))
                if take <= 0:
                    continue

                exec_price = float(self.slippage.apply(side, touch_price, qty=take))
                fills.append({"timestamp": pd.Timestamp(ts).isoformat(), "qty": take, "price": exec_price})
                total_cost += take * exec_price
                filled += take
                remaining -= take

                # call fill hook for simulated fills
                self._call_fill_hook(None, {"timestamp": pd.Timestamp(ts).isoformat(), "qty": take, "price": exec_price})

            avg_price = float(total_cost / filled) if filled > 0 else 0.0
            return {"filled_quantity": float(filled), "avg_price": float(avg_price), "fills": fills}

        fr: FillResult = simulate_partial_fill(side=side, order_qty=qty, order_price=float(ohlcv.iloc[start_loc]["close"] if start_loc < len(ohlcv) else ohlcv["close"].iloc[0]), ticks=ticks)
        fills_out = [{"timestamp": f.timestamp.isoformat(), "qty": f.qty, "price": f.price} for f in fr.fills]
        for f in fills_out:
            self._call_fill_hook(None, f)
        return {"filled_quantity": float(fr.filled_quantity), "avg_price": float(fr.avg_price), "fills": fills_out}

    def _simulate_and_apply_to_order(self, order: Order, ohlcv: pd.DataFrame, when: Optional[pd.Timestamp] = None) -> None:
        """
        Internal helper: simulate fills for the provided stored Order object and apply fills to it.
        Calls fill_hook for each applied fill.
        """
        if ohlcv is None or ohlcv.empty:
            return

        if when is None:
            try:
                when = ohlcv.index[0]
            except Exception:
                when = pd.Timestamp.utcnow()

        try:
            start_loc = ohlcv.index.get_loc(when)
        except Exception:
            start_loc = ohlcv.index.searchsorted(when)

        ticks = bars_to_ticks(ohlcv.iloc[start_loc:])

        # If slippage model provided, use that path (book consumption)
        if self.slippage is not None:
            remaining = order.remaining()
            for ts, row in ticks.sort_index().iterrows():
                if remaining <= 0:
                    break
                if str(order.side).upper().startswith("B"):
                    side_size = float(row.get("ask_size", 0.0))
                    touch_price = float(row.get("ask", float(order.price)))
                else:
                    side_size = float(row.get("bid_size", 0.0))
                    touch_price = float(row.get("bid", float(order.price)))

                available = min(remaining, side_size)
                if available <= 0:
                    continue

                take = float(math.floor(available))
                if take <= 0:
                    continue

                exec_price = float(self.slippage.apply(order.side, touch_price, qty=take))
                order.apply_fill(take, exec_price)
                remaining -= take
                fill_dict = {"timestamp": pd.Timestamp(ts).isoformat(), "qty": take, "price": exec_price}
                self._call_fill_hook(order.order_id, fill_dict)
            return

        # Fallback to volumetric simulation
        fr: FillResult = simulate_partial_fill(side=order.side, order_qty=order.remaining(), order_price=float(order.price), ticks=ticks)
        for f in fr.fills:
            order.apply_fill(f.qty, f.price)
            self._call_fill_hook(order.order_id, {"timestamp": pd.Timestamp(f.timestamp).isoformat(), "qty": f.qty, "price": f.price})

    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Return the stored Order object for order_id, or None if not found.
        """
        return self._orders.get(order_id)

    def run_to_end(self) -> None:
        """
        Process stored orders that are not yet fully filled.
        This will iterate through stored orders and simulate fills for any with remaining quantity.
        """
        if isinstance(self.price_bars, dict):
            # price_bars can be per-symbol frames; map symbol -> df
            price_map = self.price_bars
        else:
            # single-frame provided; same frame used for all symbols
            price_map = None

        for oid, order in list(self._orders.items()):
            if order.remaining() <= 0:
                continue
            # find relevant ohlcv
            if price_map is None:
                ohlcv = self.price_bars
            else:
                ohlcv = price_map.get(order.symbol)

            if ohlcv is None or ohlcv.empty:
                logger.debug("run_to_end: no market data for %s (order %s)", order.symbol, oid)
                continue

            # run simulation from beginning of available data
            try:
                self._simulate_and_apply_to_order(order, ohlcv, when=ohlcv.index[0])
            except Exception:
                logger.exception("run_to_end: simulation error for order %s", oid)

    def summary(self) -> Dict[str, Any]:
        """
        Return a small summary dict about tracked orders.

        Keys (kept/backwards-compatible):
          - n_orders: int (legacy key expected by tests)
          - total_orders: int
          - by_status: dict mapping status_name -> count
          - total_filled_qty: float
          - avg_fill_price: float or None
          - orders: list of small per-order dicts (order_id, symbol, side, qty, filled_qty, status, avg_fill_price)
        """
        total_orders = len(self._orders)
        by_status: Dict[str, int] = {}
        total_filled_qty = 0.0
        weighted_price_sum = 0.0
        price_qty_sum = 0.0
        orders_list = []

        for oid, o in self._orders.items():
            # map internal statuses to a small set for friendly reporting
            status = o.status
            if status == "partially_filled":
                friendly = "open"
            else:
                friendly = status

            by_status[friendly] = by_status.get(friendly, 0) + 1

            total_filled_qty += float(o.filled_qty or 0.0)
            if o.avg_fill_price:
                weighted_price_sum += float(o.avg_fill_price) * float(o.filled_qty or 0.0)
                price_qty_sum += float(o.filled_qty or 0.0)

            orders_list.append({
                "order_id": oid,
                "symbol": o.symbol,
                "side": o.side,
                "qty": float(o.quantity),
                "filled_qty": float(o.filled_qty),
                "status": friendly,
                "avg_fill_price": float(o.avg_fill_price) if o.avg_fill_price is not None else None,
            })

        avg_fill_price = float(weighted_price_sum / price_qty_sum) if price_qty_sum > 0 else None

        # include legacy key 'n_orders' expected by tests (alias to total_orders)
        return {
            "n_orders": total_orders,
            "total_orders": total_orders,
            "by_status": by_status,
            "total_filled_qty": total_filled_qty,
            "avg_fill_price": avg_fill_price,
            "orders": orders_list,
        }


# Export names expected by tests
__all__ = [
    "Backtester",
    "FixedTickSlippage",
    "PercentSlippage",
    "BacktesterCore",
    "Order",
    "FillEvent",
    "VolumetricImpact",
]
