# examples/strategies/simple_mean_reversion.py
"""
A tiny mean-reversion strategy example.
- Keeps a rolling window simple moving average, places a mock buy when price < sma - threshold,
  places a mock sell when price > sma + threshold.

This version prefers ctx.order_manager (async-aware wrapper) if provided, else falls back to ctx.order_client (sync).
"""

from collections import deque
from typing import Dict, Any
from data.strategy import Strategy, StrategyContext
from data.registry import register_strategy
import asyncio
import logging

log = logging.getLogger(__name__)


@register_strategy("simple_mean_reversion")
class SimpleMeanReversion(Strategy):
    def __init__(self, ctx: StrategyContext):
        super().__init__(ctx)
        cfg = ctx.config
        self.window = int(cfg.get("window", 5))
        self.threshold = float(cfg.get("threshold", 0.5))
        self.prices = deque(maxlen=self.window)
        # prefer order_manager if provided
        self.om = getattr(ctx, "order_manager", None)
        self.client = getattr(ctx, "order_client", None)

    def on_start(self):
        super().on_start()
        self.logger.info("SimpleMeanReversion starting: window=%s threshold=%s", self.window, self.threshold)

    def _place_sync(self, side: str, symbol: str, price: float):
        # direct sync fallback using client
        if not self.client:
            self.logger.warning("No order client available; skipping order")
            return None
        return self.client.place_order(symbol=symbol, side=side, qty=1, price=price)

    def _place_async_fire_and_forget(self, side: str, symbol: str, price: float):
        # if we have an async order manager, call it via run_until_complete if loop not running
        # but in practice dispatcher runs a background loop; we simply schedule via asyncio.run_coroutine_threadsafe
        if not self.om:
            return self._place_sync(side, symbol, price)
        # If order_manager is AsyncOrderManager, it exposes coroutine-based methods.
        # Try to call place_order coroutine safely:
        try:
            coro = self.om.place_order(symbol=symbol, side=side, qty=1, price=price, idempotency_key=None)
            # place without awaiting; schedule on loop if available
            # If om has sync accessor 'sync', it's not async; fallback handled by coroutine wrapper raising.
            # Use asyncio.create_task if called from within an event loop; otherwise use run_coroutine_threadsafe if loop present.
            # Best-effort: if we are in an event loop, create task; otherwise run via asyncio.run in a new loop for fire-and-forget.
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop:
                # we're in an event loop — create background task
                asyncio.create_task(coro)
            else:
                # not in event loop — run in new loop but non-blocking: use asyncio.run in a thread
                # schedule via asyncio.run_coroutine_threadsafe if AsyncOrderManager has an executor/loop; else run in a new thread
                # For safety here, run it synchronously (it's rare) — but we keep it minimal
                asyncio.run(coro)
            return {"status": "SCHEDULED"}
        except Exception:
            # if the order manager isn't async or something failed, fallback to sync place
            try:
                sync_om = getattr(self.om, "sync", None)
                if sync_om:
                    return sync_om().place_order(symbol=symbol, side=side, qty=1, price=price)
            except Exception:
                self.logger.exception("Failed to place order both async and sync fallback")
            return None

    def on_tick(self, tick: Dict[str, Any]) -> None:
        price = float(tick.get("price"))
        self.prices.append(price)
        if len(self.prices) < self.window:
            return
        sma = sum(self.prices) / len(self.prices)
        # buy signal
        if price < sma - self.threshold:
            resp = self._place_async_fire_and_forget("BUY", tick.get("symbol"), price)
            self.logger.info("BUY scheduled: %s (price=%s sma=%s)", getattr(resp, "get", lambda k: None)("order_id") if isinstance(resp, dict) else resp, price, sma)
        elif price > sma + self.threshold:
            resp = self._place_async_fire_and_forget("SELL", tick.get("symbol"), price)
            self.logger.info("SELL scheduled: %s (price=%s sma=%s)", getattr(resp, "get", lambda k: None)("order_id") if isinstance(resp, dict) else resp, price, sma)
