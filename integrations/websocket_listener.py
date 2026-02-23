"""
Minimal websocket listener abstraction for tick ingestion.

The real implementation would use `websockets` or the provider SDK.
For tests we allow injecting a message source (iterable/coroutine).
"""
import asyncio
import logging
from typing import Callable, Any, AsyncIterable, Iterable

logger = logging.getLogger(__name__)

class WebsocketListener:
    def __init__(self, message_source: Optional[Any] = None):
        """
        message_source:
          - in production: an async generator that yields json messages
          - in tests: a simple iterable or async iterable
        """
        self._source = message_source
        self._running = False

    async def _aiter_from_source(self):
        src = self._source
        if src is None:
            return
        # if it's an async iterable
        if hasattr(src, "__aiter__"):
            async for msg in src:
                yield msg
            return
        # if it's a normal iterable, convert to async
        for msg in src:
            yield msg

    async def run(self, handler: Callable[[dict], Any]) -> None:
        """
        Run listener and call handler(message) for each incoming message.
        Handler may be sync or async.
        """
        self._running = True
        try:
            async for msg in self._aiter_from_source():
                try:
                    res = handler(msg)
                    if asyncio.iscoroutine(res):
                        await res
                except Exception as e:
                    logger.exception("handler failed: %s", e)
                if not self._running:
                    break
        finally:
            self._running = False

    def stop(self):
        self._running = False
