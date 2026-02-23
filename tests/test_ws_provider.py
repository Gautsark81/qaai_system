# tests/test_ws_provider.py
import asyncio
import json
import logging
import pytest
import websockets
from modules.dhan.ws_provider import WsProvider

pytestmark = pytest.mark.asyncio

# Reduce websockets server logs to avoid JSON-serialization issues from project logger
logging.getLogger("websockets.server").propagate = False
logging.getLogger("websockets.server").setLevel(logging.WARNING)


async def _resolve_ws_from_args(*args):
    """
    Given whatever the server passed to the handler, return (websocket, path)
    Handles:
      - (websocket, path)
      - single connection-like object where `.accept()` returns websocket (newer)
      - single websocket-like object
    """
    if len(args) == 2:
        return args[0], args[1]
    if len(args) == 1:
        obj = args[0]
        # if it's already a websocket-like object (has recv/send), return it
        if hasattr(obj, "recv") and hasattr(obj, "send"):
            return obj, None
        # if it exposes accept(), call it
        if hasattr(obj, "accept"):
            ws = await obj.accept()
            return ws, None
    raise RuntimeError("Cannot resolve websocket from server handler args")


async def mock_server_handler(*args):
    ws, path = await _resolve_ws_from_args(*args)
    try:
        async for text in ws:
            try:
                msg = json.loads(text)
            except Exception:
                await ws.send(json.dumps({"error": "bad_json"}))
                continue

            if msg.get("op") == "subscribe":
                await ws.send(json.dumps({"type": "subscribed", "payload": msg}))
                for i in range(3):
                    await asyncio.sleep(0.02)
                    await ws.send(json.dumps({"type": "tick", "symbol": msg.get("symbol"), "seq": i}))
            elif msg.get("op") == "ping":
                await ws.send(json.dumps({"type": "pong"}))
            else:
                await ws.send(json.dumps({"type": "echo", "payload": msg}))
    except websockets.ConnectionClosed:
        return


async def test_ws_provider_receives_messages():
    server = await websockets.serve(mock_server_handler, "127.0.0.1", 9001)
    received = []

    async def inbound_cb(msg):
        received.append(msg)

    provider = WsProvider("ws://127.0.0.1:9001/ws", inbound_cb=inbound_cb, ping_interval=1.0, ping_timeout=1.0, reconnect_backoff_base=0.1)
    await provider.start()
    await provider.subscribe("tick:R1", {"op": "subscribe", "channel": "ticks", "symbol": "FOO"})
    await asyncio.sleep(0.35)
    await provider.stop()
    server.close()
    await server.wait_closed()

    types = [m.get("type") for m in received]
    assert "subscribed" in types
    assert types.count("tick") >= 3


async def one_close_server_handler(*args):
    ws, path = await _resolve_ws_from_args(*args)
    try:
        async for text in ws:
            msg = json.loads(text)
            if msg.get("op") == "subscribe":
                await ws.send(json.dumps({"type": "subscribed", "payload": msg}))
                await asyncio.sleep(0.05)
                await ws.close()
                return
    except websockets.ConnectionClosed:
        return


async def test_ws_provider_reconnects():
    server = await websockets.serve(one_close_server_handler, "127.0.0.1", 9002)
    received = []

    async def inbound_cb(msg):
        received.append(msg)

    provider = WsProvider("ws://127.0.0.1:9002/ws", inbound_cb=inbound_cb, reconnect_backoff_base=0.05, reconnect_backoff_cap=0.2, ping_interval=0.5)
    await provider.start()
    await provider.subscribe("tick:R2", {"op": "subscribe", "channel": "ticks", "symbol": "BAR"})
    await asyncio.sleep(0.6)
    await provider.stop()
    server.close()
    await server.wait_closed()

    types = [m.get("type") for m in received]
    assert "subscribed" in types
