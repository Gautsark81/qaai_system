# modules/dhan/ws_provider.py
from __future__ import annotations
import asyncio
import json
import logging
import random
import time
from typing import Optional, Callable, Dict, Any, Set, Awaitable

import websockets
from websockets import ConnectionClosedError

logger = logging.getLogger(__name__)
InboundCallback = Callable[[Dict[str, Any]], Awaitable[None]]


class WsProvider:
    def __init__(self, url: str, inbound_cb: Optional[InboundCallback] = None,
                 auth_headers: Optional[Dict[str, str]] = None,
                 auth_payload: Optional[Dict[str, Any]] = None,
                 ping_interval: float = 20.0,
                 ping_timeout: float = 10.0,
                 reconnect_backoff_base: float = 0.5,
                 reconnect_backoff_cap: float = 30.0,
                 jitter: float = 0.2,
                 max_reconnect_attempts: Optional[int] = None,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        self.url = url
        self.inbound_cb = inbound_cb
        self.auth_headers = auth_headers or {}
        self.auth_payload = auth_payload
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.reconnect_backoff_base = reconnect_backoff_base
        self.reconnect_backoff_cap = reconnect_backoff_cap
        self.jitter = jitter
        self.max_reconnect_attempts = max_reconnect_attempts

        self.loop = loop or asyncio.get_event_loop()
        self._ws = None  # connection object from websockets.connect

        self._running = False
        self._runner_task: Optional[asyncio.Task] = None
        self._recv_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None

        self._subscriptions: Set[str] = set()
        self._subscription_payloads: Dict[str, Dict[str, Any]] = {}

        self.connect_count = 0
        self.disconnect_count = 0
        self.recv_count = 0
        self._lock = asyncio.Lock()

        self._stop_event = asyncio.Event()

    async def start(self):
        if self._running:
            return
        self._running = True
        self._stop_event.clear()
        self._runner_task = self.loop.create_task(self._runner())
        logger.info("WsProvider started for %s", self.url)

    async def stop(self):
        if not self._running:
            return
        self._running = False
        self._stop_event.set()
        if self._recv_task:
            self._recv_task.cancel()
        if self._ping_task:
            self._ping_task.cancel()
        if self._runner_task:
            self._runner_task.cancel()
        # close websocket if possible
        try:
            if self._ws is not None:
                await getattr(self._ws, "close")()
        except Exception:
            logger.exception("Error while closing websocket")
        logger.info("WsProvider stopped for %s", self.url)

    async def subscribe(self, key: str, payload: Dict[str, Any]):
        async with self._lock:
            self._subscription_payloads[key] = payload
            self._subscriptions.add(key)
            if self._is_connected():
                try:
                    await self._send_json(payload)
                except Exception:
                    logger.exception("subscribe immediate send failed")

    async def unsubscribe(self, key: str, payload: Optional[Dict[str, Any]] = None):
        async with self._lock:
            self._subscriptions.discard(key)
            self._subscription_payloads.pop(key, None)
            if payload and self._is_connected():
                try:
                    await self._send_json(payload)
                except Exception:
                    logger.exception("unsubscribe immediate send failed")

    def _is_connected(self) -> bool:
        if self._ws is None:
            return False
        open_attr = getattr(self._ws, "open", None)
        if isinstance(open_attr, bool):
            return open_attr
        closed_attr = getattr(self._ws, "closed", None)
        if isinstance(closed_attr, bool):
            return not closed_attr
        state = getattr(self._ws, "state", None)
        if isinstance(state, str):
            return state.upper() == "OPEN"
        return True

    async def _runner(self):
        attempt = 0
        while self._running and (self.max_reconnect_attempts is None or attempt <= (self.max_reconnect_attempts or 0)):
            try:
                await self._connect()
                attempt = 0
                await self._stop_event.wait()
                break
            except asyncio.CancelledError:
                break
            except Exception as exc:
                attempt += 1
                self.disconnect_count += 1
                backoff = min(self.reconnect_backoff_cap, self.reconnect_backoff_base * (2 ** (attempt - 1)))
                backoff = backoff * (1 + self.jitter * (random.random() * 2 - 1))
                logger.warning("WsProvider: connection error (attempt %s): %s — reconnect in %.2fs", attempt, exc, backoff)
                await asyncio.sleep(backoff)
                continue
        logger.info("WsProvider runner exiting for %s", self.url)

    async def _maybe_send_auth(self):
        if self.auth_payload and self._is_connected():
            try:
                await self._send_json(self.auth_payload)
            except Exception:
                logger.exception("failed to send auth payload")

    async def _connect(self):
        logger.info("WsProvider connecting to %s", self.url)
        # do not pass extra_headers to avoid compatibility issues
        self._ws = await websockets.connect(self.url, ping_interval=None)
        self.connect_count += 1
        logger.info("WsProvider connected to %s", self.url)

        # small delay to avoid racing the server's handler setup in tests/environments
        await asyncio.sleep(0.02)

        # optional auth
        await self._maybe_send_auth()

        # send existing subscriptions (retry on failure — allow exceptions to bubble and trigger reconnect)
        async with self._lock:
            for key, payload in list(self._subscription_payloads.items()):
                try:
                    await self._send_json(payload)
                except ConnectionClosedError:
                    logger.warning("connection closed while re-subscribing %s", key)
                    raise
                except Exception:
                    logger.exception("failed to re-subscribe %s", key)

        # spawn background tasks
        self._recv_task = self.loop.create_task(self._recv_loop())
        self._ping_task = self.loop.create_task(self._ping_loop())

        # wait until one of them fails/cancels
        done, pending = await asyncio.wait([self._recv_task, self._ping_task], return_when=asyncio.FIRST_EXCEPTION)
        for t in pending:
            t.cancel()
        for t in done:
            if t.cancelled():
                continue
            exc = t.exception()
            if exc:
                raise exc

    async def _ping_loop(self):
        try:
            while True:
                await asyncio.sleep(self.ping_interval)
                if not self._is_connected():
                    logger.debug("ping_loop: ws not open")
                    return
                try:
                    pong_waiter = await getattr(self._ws, "ping")()
                    await asyncio.wait_for(pong_waiter, timeout=self.ping_timeout)
                except asyncio.TimeoutError:
                    logger.warning("ping timeout, closing websocket to trigger reconnect")
                    try:
                        await getattr(self._ws, "close")()
                    except Exception:
                        pass
                    return
                except ConnectionClosedError:
                    logger.info("connection closed during ping")
                    return
                except Exception:
                    logger.exception("unexpected ping error")
                    return
        except asyncio.CancelledError:
            return

    async def _recv_loop(self):
        try:
            async for raw in self._ws:
                self.recv_count += 1
                try:
                    if isinstance(raw, (bytes, bytearray)):
                        text = raw.decode("utf-8")
                    else:
                        text = raw
                    msg = json.loads(text)
                except Exception:
                    logger.exception("failed to parse incoming message: %r", raw)
                    continue

                if self.inbound_cb:
                    try:
                        await self.inbound_cb(msg)
                    except Exception:
                        logger.exception("inbound callback raised exception")
        except asyncio.CancelledError:
            return
        except ConnectionClosedError:
            logger.info("websocket connection closed")
            return
        except Exception:
            logger.exception("recv loop crashed")
            raise

    async def _send_json(self, payload: Dict[str, Any]):
        if not self._is_connected():
            raise ConnectionError("websocket not connected")
        text = json.dumps(payload)
        try:
            await getattr(self._ws, "send")(text)
        except ConnectionClosedError:
            # bubble up to allow reconnect path
            raise
        except Exception:
            logger.exception("send failed")
            raise

    def subscribe_nowait(self, key: str, payload: Dict[str, Any]) -> None:
        asyncio.run_coroutine_threadsafe(self.subscribe(key, payload), self.loop)

    async def run_forever(self):
        await self.start()
        try:
            await self._runner_task
        finally:
            await self.stop()
