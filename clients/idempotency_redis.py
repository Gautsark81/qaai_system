# clients/idempotency_redis.py
"""
Redis-backed idempotency store.

Provides a dict-like interface:
- __contains__(key)
- __getitem__(key)
- __setitem__(key, value)
- get(key, default=None)
- keys()
- close()

Implementation notes:
- Values stored as JSON strings.
- Uses redis-py client if available.
- This module intentionally keeps a minimal API so OrderManager can use it interchangeably with SqliteIdempotencyStore or a dict.
"""

from __future__ import annotations
import json
import logging
from typing import Optional, Dict, Any, Iterable

logger = logging.getLogger(__name__)

try:
    import redis  # redis-py
    _HAS_REDIS = True
except Exception:
    _HAS_REDIS = False
    redis = None  # type: ignore


class RedisIdempotencyStore:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, prefix: str = "amats:idemp:"):
        if not _HAS_REDIS:
            raise RuntimeError("redis package not installed; install 'redis' to use RedisIdempotencyStore")
        self._client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self._prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def __contains__(self, key: str) -> bool:
        try:
            return self._client.exists(self._key(key)) == 1
        except Exception:
            logger.exception("Redis __contains__ failed for key %s", key)
            return False

    def __getitem__(self, key: str) -> Dict[str, Any]:
        v = self._client.get(self._key(key))
        if v is None:
            raise KeyError(key)
        try:
            return json.loads(v)
        except Exception:
            # fallback: return raw string
            return {"raw": v}

    def __setitem__(self, key: str, value: Dict[str, Any]) -> None:
        try:
            self._client.set(self._key(key), json.dumps(value))
        except Exception:
            logger.exception("Failed to set idempotency key %s", key)
            raise

    def get(self, key: str, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def keys(self) -> Iterable[str]:
        try:
            raw = self._client.keys(f"{self._prefix}*")
            # strip prefix
            return [k[len(self._prefix):] for k in raw]
        except Exception:
            logger.exception("Failed to fetch keys from RedisIdempotencyStore")
            return []

    def close(self):
        try:
            self._client.close()
        except Exception:
            pass
