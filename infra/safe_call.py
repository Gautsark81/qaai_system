# infra/safe_call.py
from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Iterable, Optional, Tuple, Type

from .exceptions import QaaiSystemError
from .logging import get_logger

logger = get_logger(__name__)


async def safe_call_async(
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    retries: int = 3,
    backoff_base: float = 0.5,
    backoff_factor: float = 2.0,
    timeout: Optional[float] = None,
    retry_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    swallow_exceptions: bool = False,
    **kwargs: Any,
) -> Any:
    """
    Run an async call with retries, exponential backoff and optional timeout.

    This should be used for:
    - DhanHQ calls
    - Redis ops
    - Network / IO heavy infrastructure calls
    """
    attempt = 0
    while True:
        try:
            coro = func(*args, **kwargs)
            if timeout is not None:
                return await asyncio.wait_for(coro, timeout=timeout)
            return await coro
        except retry_exceptions as exc:  # type: ignore[misc]
            attempt += 1
            if attempt > retries:
                logger.error(
                    "safe_call_async_giveup",
                    extra={
                        "func": getattr(func, "__name__", str(func)),
                        "attempt": attempt,
                        "retries": retries,
                        "error": str(exc),
                    },
                )
                if swallow_exceptions:
                    return None
                raise
            delay = backoff_base * (backoff_factor ** (attempt - 1))
            logger.warning(
                "safe_call_async_retry",
                extra={
                    "func": getattr(func, "__name__", str(func)),
                    "attempt": attempt,
                    "retries": retries,
                    "delay": delay,
                    "error": str(exc),
                },
            )
            await asyncio.sleep(delay)


def safe_call_sync(
    func: Callable[..., Any],
    *args: Any,
    retries: int = 3,
    backoff_base: float = 0.5,
    backoff_factor: float = 2.0,
    retry_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    swallow_exceptions: bool = False,
    **kwargs: Any,
) -> Any:
    """
    Sync version used for CPU-bound or simple infra calls.
    """
    attempt = 0
    while True:
        try:
            return func(*args, **kwargs)
        except retry_exceptions as exc:  # type: ignore[misc]
            attempt += 1
            if attempt > retries:
                logger.error(
                    "safe_call_sync_giveup",
                    extra={
                        "func": getattr(func, "__name__", str(func)),
                        "attempt": attempt,
                        "retries": retries,
                        "error": str(exc),
                    },
                )
                if swallow_exceptions:
                    return None
                raise
            delay = backoff_base * (backoff_factor ** (attempt - 1))
            logger.warning(
                "safe_call_sync_retry",
                extra={
                    "func": getattr(func, "__name__", str(func)),
                    "attempt": attempt,
                    "retries": retries,
                    "delay": delay,
                    "error": str(exc),
                },
            )
            import time as _time

            _time.sleep(delay)
