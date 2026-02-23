"""
Async Redis consumer example that subscribes to market:ticks and writes to
downstream sinks (e.g. DB, kafka) or emits via websocket channels.

This uses redis.asyncio to avoid blocking the event loop.
"""

import os
import asyncio
import json
import logging
from typing import Callable

import redis.asyncio as aioredis

logger = logging.getLogger("redis_consumer")
logger.setLevel(logging.INFO)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CHANNEL = os.getenv("REDIS_CHANNEL", "market:ticks")


async def handle_message(msg: dict):
    # transform and send to DB/Kafka/etc.
    # Example: print and ack
    try:
        # simple pipeline: parse and log
        data = msg if isinstance(msg, dict) else json.loads(msg)
        # TODO: send to DB / metrics / model pipeline
        logger.info("tick -> %s %s", data.get("symbol"), data.get("timestamp"))
    except Exception as e:
        logger.exception("handler failed: %s", e)


async def consumer_loop(handler: Callable[[dict], None]):
    r = aioredis.from_url(REDIS_URL)
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(CHANNEL)
    logger.info("Subscribed to %s", CHANNEL)
    try:
        async for raw in pubsub.listen():
            if raw is None:
                await asyncio.sleep(0.01)
                continue
            # raw looks like {'type':'message','channel':b'market:ticks','data':b'...'}
            if raw.get("type") == "message":
                payload = raw.get("data")
                try:
                    if isinstance(payload, bytes):
                        payload = payload.decode("utf-8")
                    data = json.loads(payload)
                except Exception:
                    data = payload
                await handler(data)
    finally:
        await pubsub.unsubscribe(CHANNEL)
        await r.close()


if __name__ == "__main__":
    asyncio.run(consumer_loop(handle_message))
