"""
Router: core market loop that reads ticks from Dhan (or stub), forwards to strategies.
- Keeps an internal asyncio.Task for the market loop.
- Small, robust handlers with try/except
"""
import asyncio
import logging
import os
from typing import Optional

logger = logging.getLogger("router")

class Router:
    def __init__(self, dhan_client, poll_interval: float = 0.01):
        self.dhan = dhan_client
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self.poll_interval = poll_interval
        self._stale_count = 0

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._market_loop())

    async def stop(self):
        self._running = False
        if self._task:
            await self._task
        logger.info("router stopped")

    async def _market_loop(self):
        logger.info("market loop started")
        while self._running:
            try:
                # In production: subscribe/receive websocket messages
                # Here: demo polling of a REST endpoint or stub
                if os.getenv("TRADING_ENV", "paper") == "paper":
                    # generate synthetic tick
                    tick = {"symbol": "SYNTH", "price": 100.0}
                    await self.handle_tick(tick)
                    await asyncio.sleep(self.poll_interval)
                    continue

                # Example: call client.get("market/ticker") - adapt to your API
                try:
                    data = await self.dhan.get("v2/market/ticker")
                except Exception as e:
                    logger.warning("market fetch failed: %s", e)
                    await asyncio.sleep(min(1.0, self.poll_interval * 10))
                    continue

                # data should be iterable; handle accordingly
                if isinstance(data, dict) and data.get("tick"):
                    await self.handle_tick(data["tick"])
                elif isinstance(data, list):
                    for tick in data:
                        await self.handle_tick(tick)
                else:
                    # unknown payload
                    logger.debug("unknown market payload shape: %s", type(data))
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                logger.info("market loop cancelled")
                break
            except Exception:
                logger.exception("Unhandled error in market loop, continuing")
                await asyncio.sleep(0.5)
        logger.info("market loop exiting")

    async def handle_tick(self, tick):
        try:
            # Example transform: validate and forward to strategy manager / order manager
            symbol = tick.get("symbol") or tick.get("s")
            price = tick.get("price") or tick.get("lastPrice") or tick.get("p")
            if symbol is None or price is None:
                logger.debug("tick missing fields: %s", tick)
                return
            # TODO: dispatch to strategy manager (import and call)
            logger.debug("tick %s @ %s", symbol, price)
            # small example: if price crosses threshold then send stubbed order
            thresh = float(os.getenv("EXAMPLE_ORDER_THRESHOLD", "1000000"))
            if float(price) < thresh and os.getenv("EXAMPLE_PLACE_ORDERS", "false").lower() in ("true", "1"):
                order = {"symbol": symbol, "qty": 1, "price": price, "side": "BUY"}
                await self.dhan.send_order(order)
        except Exception:
            logger.exception("error in handle_tick")
