# integrations/dhan_live.py
"""
Async connector for DhanHQ Live Market feed.

Key features:
 - Uses an asyncio.Queue for parsed messages (conn.messages_queue)
 - Robust reconnect/backoff
 - Accepts `connect_callable` injection for platform-specific websockets
   handling (useful for tests or special auth headers).
 - By default the API key is appended to the feed_url as a query param
   to avoid passing extra kwargs into event loop internals on some platforms.
"""
import asyncio
import json
import logging
from typing import Optional, Callable, Awaitable, Any
import types

logger = logging.getLogger(__name__)

DEFAULT_RECONNECT_BACKOFF = [1, 2, 4, 8, 30]  # seconds


class DhanLiveConnector:
    def __init__(
        self,
        feed_url: str,
        api_key: str,
        messages: Optional[asyncio.Queue] = None,
        on_message: Optional[Callable[[dict], None]] = None,
        connect_callable: Optional[Callable[..., Awaitable[Any]]] = None,
    ):
        """
        feed_url: base websocket URL (e.g. "wss://live.dhan.co/market")
        api_key: API key/token. By default appended as query param.
        messages: optional asyncio.Queue to push parsed messages into.
        on_message: optional callback(msg) executed for each parsed message.
        connect_callable: optional callable used to open the websocket.
          signature: awaitable = connect_callable(url, **kwargs)
          It should return an object that is either:
            - an async context manager that yields an async-iterable websocket (like websockets.connect)
            - or a coroutine returning an object that supports async iteration.
        """
        self.feed_url = feed_url
        self.api_key = api_key
        self._ws = None
        self._task: Optional[asyncio.Task] = None
        self._stopped = asyncio.Event()
        self._messages = messages or asyncio.Queue()
        self.on_message = on_message
        self._backoff = DEFAULT_RECONNECT_BACKOFF[:]
        self.metrics = {"connects": 0, "reconnects": 0, "messages": 0, "last_msg_ts": None}
        # Default connect callable
        if connect_callable is None:
            try:
                import websockets  # type: ignore
                connect_callable = websockets.connect
            except Exception:
                # Fallback: minimal placeholder; user should pass a connect_callable
                async def _raise(*args, **kwargs):
                    raise RuntimeError("No websockets library available; pass connect_callable")
                connect_callable = _raise
        self._connect_callable = connect_callable

    @property
    def messages_queue(self):
        return self._messages

    async def start(self):
        if self._task and not self._task.done():
            return
        self._stopped.clear()
        self._task = asyncio.create_task(self._runner())

    async def stop(self):
        self._stopped.set()
        # try to close ws and await task
        if self._ws and hasattr(self._ws, "close"):
            try:
                maybe = self._ws.close
                if asyncio.iscoroutinefunction(maybe):
                    await maybe()
                else:
                    # if close returns coroutine
                    res = maybe()
                    if asyncio.iscoroutine(res):
                        await res
            except Exception:
                logger.exception("Error closing websocket")
        if self._task:
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _runner(self):
        """
        Main runner: connect, read messages, push into queue, handle reconnects.
        """
        backoff_idx = 0
        # Build URL with api_key appended as query param (avoid passing extra headers into loop)
        url = self.feed_url
        if self.api_key:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}api_key={self.api_key}"

        while not self._stopped.is_set():
            try:
                self.metrics["connects"] += 1
                # call the connect callable
                connectable = self._connect_callable(url, ping_interval=20, ping_timeout=10)

                # If connectable is an async context manager (like websockets.connect)
                if hasattr(connectable, "__aenter__"):
                    async with connectable as ws:
                        self._ws = ws
                        logger.info("Connected to Dhan live feed (ctx-manager)")
                        backoff_idx = 0
                        await self._read_loop(ws)
                else:
                    # Otherwise it might be a coroutine returning a ws-like object
                    maybe = connectable
                    if asyncio.iscoroutine(maybe):
                        ws = await maybe
                    else:
                        # If it's a regular object (unlikely), use it directly.
                        ws = maybe
                    self._ws = ws
                    logger.info("Connected to Dhan live feed (awaited connect)")
                    backoff_idx = 0
                    try:
                        await self._read_loop(ws)
                    finally:
                        # try close if available
                        if hasattr(ws, "close"):
                            try:
                                res = ws.close()
                                if asyncio.iscoroutine(res):
                                    await res
                            except Exception:
                                logger.debug("ws close raised")
            except asyncio.CancelledError:
                logger.info("DhanLiveConnector runner cancelled")
                raise
            except Exception as exc:
                logger.exception("Live feed connection failed, will attempt reconnect: %s", exc)
                self.metrics["reconnects"] += 1
                # backoff
                delay = self._backoff[min(backoff_idx, len(self._backoff) - 1)]
                backoff_idx += 1
                # Wait with ability to stop early
                try:
                    await asyncio.wait_for(self._stopped.wait(), timeout=delay)
                except asyncio.TimeoutError:
                    pass
        logger.info("DhanLiveConnector stopped")

    async def _read_loop(self, ws):
        """
        Read loop from websocket-like object. Supports both async iteration and an explicit recv() method.
        """
        # If the ws supports async iteration (async for), prefer that.
        if hasattr(ws, "__aiter__"):
            async for raw in ws:
                if self._stopped.is_set():
                    break
                await self._handle_raw(raw)
        else:
            # fallback to recv() loop
            recv = getattr(ws, "recv", None)
            if recv is None:
                raise RuntimeError("Websocket object has no __aiter__ or recv()")
            while not self._stopped.is_set():
                raw = await recv()
                await self._handle_raw(raw)

    async def _handle_raw(self, raw):
        # parse and push
        try:
            if isinstance(raw, (bytes, bytearray)):
                raw = raw.decode("utf-8")
            msg = json.loads(raw)
        except Exception as e:
            logger.exception("Failed to parse message: %s", e)
            return
        self.metrics["messages"] += 1
        self.metrics["last_msg_ts"] = asyncio.get_event_loop().time()
        # deliver
        try:
            await self._messages.put(msg)
        except Exception:
            logger.exception("Failed to put message on queue")
        if self.on_message:
            try:
                self.on_message(msg)
            except Exception:
                logger.exception("on_message handler failed")
