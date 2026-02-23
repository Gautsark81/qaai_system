# services/live_tick_service.py
"""
Live Tick Streaming Microservice
- Subscribes to DhanHQ live market feed (via dhanhq SDK when available)
- Normalizes packets into TickStore format:
    {'symbol', 'timestamp', 'price', 'size', 'raw_type', 'raw_json'}
- Publishes to:
    - Redis list/channel (if redis client provided)
    - or directly into TickStore (if provided)
- Runs as asyncio service; supports graceful shutdown.
"""

from __future__ import annotations
import asyncio
import json
import logging
import time
from typing import Any, Iterable, Optional, Dict

logger = logging.getLogger(__name__)

# try import SDK
try:
    from dhanhq import DhanContext, MarketFeed  # type: ignore
    _HAS_SDK = True
except Exception:
    _HAS_SDK = False

# optional redis client
try:
    import redis  # type: ignore
    _HAS_REDIS = True
except Exception:
    _HAS_REDIS = False

# Normalizer utility
def normalize_packet(pkt: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convert DhanHQ packet into TickStore tick dict:
    {'symbol','timestamp','price','size','raw_type','raw_json'}
    The mapping will use security_id -> symbol mapping if you have one; for now map to security_id str.
    """
    pkt_type = pkt.get("type", "").lower()
    sec_id = pkt.get("security_id")
    # fallback symbol = str(security_id)
    symbol = str(sec_id)
    # choose price and size heuristics based on packet type
    if "LTP" in pkt:
        price = float(pkt.get("LTP"))
    elif "ltp" in pkt:
        price = float(pkt.get("ltp"))
    elif "close" in pkt:
        price = float(pkt.get("close"))
    else:
        return None
    size = int(pkt.get("LTQ", pkt.get("ltq", pkt.get("size", 0))))
    # attempt to parse time string LTT if available
    ts = pkt.get("timestamp") or pkt.get("ts")
    if ts is None:
        # try LTT (hh:mm:ss) convert to today's epoch
        LTT = pkt.get("LTT")
        if LTT:
            # parse today's date + LTT
            try:
                today = time.strftime("%Y-%m-%d")
                dt = f"{today} {LTT}"
                ts = time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S"))
            except Exception:
                ts = time.time()
        else:
            ts = time.time()
    # ensure numeric timestamp
    try:
        ts = float(ts)
    except Exception:
        ts = time.time()
    return {
        "symbol": symbol,
        "timestamp": ts,
        "price": float(price),
        "size": int(size) if size is not None else 0,
        "raw_type": pkt.get("type"),
        "raw_json": pkt,
    }

class LiveTickService:
    def __init__(self, dhan_context: Any = None, instruments: Optional[Iterable]=None, tick_store: Any = None, redis_client: Any = None):
        """
        dhan_context: instance of DhanContext or credentials tuple if SDK is used
        instruments: iterable of (exchange_segment, security_id, subscription_type) per Dhan API
        tick_store: optional TickStore instance (preferred)
        redis_client: optional redis.Redis instance (if provided, we publish ticks to redis list/channel)
        """
        self.dhan_context = dhan_context
        self.instruments = instruments or []
        self.tick_store = tick_store
        self.redis_client = redis_client
        self._running = False
        self._loop = None
        self._task = None
        self._feed = None

    async def _sdk_runner(self):
        """Run feed using dhanhq SDK (blocking call to run_forever wrapped in thread)"""
        # MarketFeed object provides run_forever() and get_data() in your sample
        # We'll create it in a thread-safe manner and call get_data periodically
        loop = asyncio.get_running_loop()
        def create_feed():
            # if dhan_context is a (client_id, token) tuple, construct DhanContext
            if isinstance(self.dhan_context, tuple) and len(self.dhan_context) >= 2:
                ctx = DhanContext(*self.dhan_context)
            else:
                ctx = self.dhan_context
            feed = MarketFeed(ctx, self.instruments, "v2")
            return feed
        self._feed = await loop.run_in_executor(None, create_feed)
        # feed.run_forever() is blocking; run in executor
        def run_forever_and_capture():
            try:
                self._feed.run_forever()
            except Exception:
                logger.exception("MarketFeed run_forever error")
        # run it in background thread
        fut = loop.run_in_executor(None, run_forever_and_capture)
        # Poll feed.get_data periodically
        while self._running:
            try:
                pkt = await loop.run_in_executor(None, self._feed.get_data)
                if pkt:
                    tick = normalize_packet(pkt)
                    if tick:
                        self._publish_tick(tick)
            except Exception:
                logger.exception("Error while polling MarketFeed.get_data")
            await asyncio.sleep(0.01)
        # attempt to stop feed if SDK exposes stop
        try:
            if hasattr(self._feed, "stop"):
                await loop.run_in_executor(None, self._feed.stop)
        except Exception:
            pass

    def _publish_tick(self, tick: Dict[str, Any]) -> None:
        # publish to redis if configured
        try:
            if self.redis_client is not None:
                # push JSON onto list and publish on channel
                key = f"ticks:{tick['symbol']}"
                self.redis_client.rpush(key, json.dumps(tick))
                try:
                    self.redis_client.publish("ticks", json.dumps({"symbol": tick["symbol"], "ts": tick["timestamp"]}))
                except Exception:
                    pass
                return
        except Exception:
            logger.exception("Redis publish failed; falling back to TickStore")
        # fallback: write to TickStore if available
        try:
            if self.tick_store is not None:
                self.tick_store.append_tick(tick["symbol"], tick)
                return
        except Exception:
            logger.exception("TickStore append failed")

    async def start(self):
        if self._running:
            return
        self._running = True
        if _HAS_SDK:
            self._task = asyncio.create_task(self._sdk_runner())
        else:
            # TODO: implement raw websocket fallback if desired
            logger.warning("DhanHQ SDK not available: no live feed started")
            self._task = None

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except Exception:
                pass

# CLI helper (run with `python -m services.live_tick_service`)
if __name__ == "__main__":
    import argparse, os, sys
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", required=False)
    parser.add_argument("--access-token", required=False)
    parser.add_argument("--use-redis", action="store_true")
    args = parser.parse_args()

    # Build DhanContext if SDK present
    if _HAS_SDK:
        if args.client_id and args.access_token:
            ctx = DhanContext(args.client_id, args.access_token)
        else:
            print("Please pass client-id and access-token")
            sys.exit(1)
    else:
        print("DhanHQ SDK not found. Install `dhanhq` or pip from repo.")
        sys.exit(1)

    # create tick store (fall back)
    try:
        from data.tick_store import TickStore
        ts = TickStore()
    except Exception:
        ts = None

    redis_client = None
    if args.use_redis and _HAS_REDIS:
        redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # example instrument list (user should pass actual instruments)
    instruments = [
        (1, "1333", MarketFeed.Ticker),
        (1, "11915", MarketFeed.Full),
    ]
    svc = LiveTickService(dhan_context=ctx, instruments=instruments, tick_store=ts, redis_client=redis_client)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(svc.start())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(svc.stop())
