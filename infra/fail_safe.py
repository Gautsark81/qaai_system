# infra/fail_safe.py
"""
Retry decorator with exponential backoff + jitter and a simple CircuitBreaker.
"""

import asyncio
import random
import time
import logging
from functools import wraps
from typing import Callable

logger = logging.getLogger("fail_safe")


def retry(max_attempts: int = 3, base_delay: float = 0.1, jitter: float = 0.1, exceptions=(Exception,)):
    def decorator(fn):
        if asyncio.iscoroutinefunction(fn):
            @wraps(fn)
            async def _wrap(*args, **kwargs):
                attempt = 0
                while True:
                    try:
                        return await fn(*args, **kwargs)
                    except exceptions as e:
                        attempt += 1
                        if attempt >= max_attempts:
                            logger.exception("retry: max attempts reached")
                            raise
                        delay = base_delay * (2 ** (attempt - 1)) + random.random() * jitter
                        logger.warning(f"retry: attempt {attempt} failed ({e}), sleeping {delay:.3f}s")
                        await asyncio.sleep(delay)
            return _wrap
        else:
            @wraps(fn)
            def _wrap_sync(*args, **kwargs):
                attempt = 0
                while True:
                    try:
                        return fn(*args, **kwargs)
                    except exceptions as e:
                        attempt += 1
                        if attempt >= max_attempts:
                            logger.exception("retry: max attempts reached")
                            raise
                        delay = base_delay * (2 ** (attempt - 1)) + random.random() * jitter
                        logger.warning(f"retry: attempt {attempt} failed ({e}), sleeping {delay:.3f}s")
                        time.sleep(delay)
            return _wrap_sync
    return decorator


class CircuitBreaker:
    """
    Simple circuit breaker:
    - trips after `fail_max` consecutive failures
    - stays open for `reset_timeout` seconds, then half-open probing
    """
    def __init__(self, fail_max: int = 5, reset_timeout: float = 30.0):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.fail_count = 0
        self.opened_at = None

    def _is_open(self) -> bool:
        if self.opened_at is None:
            return False
        # if timeout passed, move to half-open (treated as closed here)
        if (time.time() - self.opened_at) > self.reset_timeout:
            self.opened_at = None
            self.fail_count = 0
            return False
        return True

    def call(self, fn: Callable, *args, **kwargs):
        if self._is_open():
            raise RuntimeError("circuit open")
        try:
            res = fn(*args, **kwargs)
            # success -> reset
            self.fail_count = 0
            return res
        except Exception:
            self.fail_count += 1
            if self.fail_count >= self.fail_max:
                self.opened_at = time.time()
                logger.warning("circuit.opened")
            raise
