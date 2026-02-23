"""
ingestion/market_ingestor.py

Consumes messages from integrations.dhan_live.DhanLiveConnector, normalizes them
into an internal tick dict and pushes into an asyncio.Queue for downstream consumers.

Design:
- Nonblocking: uses async tasks and queues
- Lightweight normalization + validation
- Metrics counters for messages accepted / rejected
- Pluggable message handler callback (on_tick)
"""

import asyncio
import logging
from typing import Callable, Optional, Dict, Any
from integrations.dhan_live import DhanLiveConnector

logger = logging.getLogger(__name__)


def normalize_dhan_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convert raw Dhan Live message into internal tick format:
    {
        "type": "tick",
        "security_id": int,
        "symbol": optional str,
        "ltp": float,
        "ltq": int,
        "timestamp": "HH:MM:SS" or ISO,
        "volume": int (total),
        "depth": [ ... ] optional
    }
    Return None for messages we don't consume.
    """
    if not isinstance(msg, dict):
        return None

    t = msg.get("type", "")
    sec = msg.get("security_id") or msg.get("symbol")
    if not sec:
        return None

    try:
        if t in ("Ticker Data", "Quote Data", "Full Data"):
            out = {
                "type": "tick",
                "security_id": int(sec),
                "ltp": float(msg.get("LTP")) if msg.get("LTP") is not None else None,
                "ltq": int(msg.get("LTQ")) if msg.get("LTQ") is not None else None,
                "timestamp": msg.get("LTT"),
                "volume": int(msg.get("volume")) if msg.get("volume") is not None else None,
                "raw_type": t,
            }
            # attach depth or other fields if present
            if "depth" in msg:
                out["depth"] = msg["depth"]
            return out
        # ignore Previous Close etc by default
        return None
    except Exception:
        logger.exception("normalize_dhan_message failed for %s", msg)
        return None


class MarketIngestor:
    def __init__(
        self,
        feed_url: str,
        api_key: str,
        out_queue: Optional[asyncio.Queue] = None,
        connect_callable: Optional[Callable[..., object]] = None,
        on_tick: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        out_queue: asyncio.Queue where normalized ticks will be pushed.
        connect_callable: optional connect function to inject (useful for tests).
        on_tick: optional sync callback called for each normalized tick.
        """
        self.out_queue = out_queue or asyncio.Queue()
        self.on_tick = on_tick
        self.connector = DhanLiveConnector(
            feed_url=feed_url,
            api_key=api_key,
            messages=self.out_queue if False else None,  # we'll use our own consuming path
            connect_callable=connect_callable,
        )
        self._worker_task: Optional[asyncio.Task] = None
        self._consume_task: Optional[asyncio.Task] = None
        self.metrics = {"ingested": 0, "normalized": 0, "rejected": 0}

        # internal queue used to receive raw messages from DhanLiveConnector
        self._raw_q: asyncio.Queue = asyncio.Queue()

        # wire the connector to push into our raw queue via on_message
        def _on_msg(m):
            # schedule a put on raw_q (avoid blocking the connector)
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(asyncio.create_task, self._raw_q.put(m))
            except RuntimeError:
                # no running loop — fallback synchronous put (mostly for tests)
                try:
                    self._raw_q.put_nowait(m)
                except Exception:
                    logger.exception("Failed to put message into raw queue")

        # replace default connector's on_message
        self.connector.on_message = _on_msg

    async def start(self):
        # start connector
        await self.connector.start()
        # start consumer task
        if not self._consume_task or self._consume_task.done():
            self._consume_task = asyncio.create_task(self._consume_loop())

    async def stop(self):
        await self.connector.stop()
        if self._consume_task:
            self._consume_task.cancel()
            try:
                await self._consume_task
            except asyncio.CancelledError:
                pass

    async def _consume_loop(self):
        while True:
            raw = await self._raw_q.get()
            self.metrics["ingested"] += 1
            tick = normalize_dhan_message(raw)
            if tick is None:
                self.metrics["rejected"] += 1
                continue
            self.metrics["normalized"] += 1
            # push to out_queue for downstream consumers (feature store / DB writer)
            try:
                await self.out_queue.put(tick)
            except Exception:
                logger.exception("Failed to put normalized tick into out_queue")
            # invoke optional callback (sync)
            if self.on_tick:
                try:
                    self.on_tick(tick)
                except Exception:
                    logger.exception("on_tick callback failed")
