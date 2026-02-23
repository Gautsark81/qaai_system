# infra/redis_queue.py
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional

from .exceptions import RedisError
from .logging import get_logger

logger = get_logger(__name__)

try:
    from redis.asyncio import Redis
except ImportError as exc:  # pragma: no cover - env-specific
    Redis = Any  # type: ignore[assignment]
    _import_error = exc
else:
    _import_error = None


@dataclass
class RedisConfig:
    url: Optional[str] = None
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None


def create_redis_client(cfg: RedisConfig) -> Redis:
    if _import_error is not None:  # pragma: no cover - env-specific
        raise RedisError(
            "redis.asyncio is not installed; please `pip install redis`"
        ) from _import_error

    if cfg.url:
        return Redis.from_url(cfg.url, decode_responses=True)
    return Redis(
        host=cfg.host,
        port=cfg.port,
        db=cfg.db,
        password=cfg.password,
        decode_responses=True,
    )


class RedisPubSubChannel:
    """
    Pub/Sub wrapper for channels like 'market:ticks'.
    """

    def __init__(self, redis: Redis, channel: str) -> None:
        self._redis = redis
        self._channel = channel

    async def publish(self, message: Any) -> None:
        if not isinstance(message, str):
            message = json.dumps(message, ensure_ascii=False)
        await self._redis.publish(self._channel, message)

    async def subscribe(self) -> AsyncIterator[str]:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self._channel)
        logger.info("redis_subscribed", extra={"channel": self._channel})
        async for msg in pubsub.listen():
            if msg.get("type") != "message":
                continue
            data = msg.get("data")
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            yield data  # caller can json.loads if needed
