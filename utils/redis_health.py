# utils/redis_health.py
from typing import Optional
import redis
import socket
import logging

logger = logging.getLogger(__name__)

def check_redis_health(host: str = "localhost", port: int = 6379, timeout: float = 0.5) -> bool:
    """
    Quick health probe for Redis. Returns True if ping succeeds.
    """
    try:
        r = redis.Redis(host=host, port=port, socket_connect_timeout=timeout)
        return r.ping()
    except Exception as e:
        logger.debug("Redis health check failed: %s", e)
        return False
