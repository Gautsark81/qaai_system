import asyncio
import json
import sqlite3
import logging
import pytest
import websockets

from modules.dhan.fetcher import DhanFetcher, SeqStore

pytestmark = pytest.mark.asyncio

# Reduce websockets server noise in logs (your JSON logger may choke on internal objects)
logging.getLogger("websockets.server").propagate = False
logging.getLogger("websockets.server").setLevel(logging.WARNING)


async def _resolve_ws(ws_obj):
    """
    Accepts what websockets server passes to handler and returns websocket object.
    Works for both older (websocket, path) and newer (connection) signatures.
    """
    if isinstance(ws_obj, tuple) or isinstance(ws_obj, list):
        return ws_obj[0]
    # try accept()
    if hasattr(ws_obj, "accept"):
        return await ws_obj.accept()
    return ws_obj


async def mock_server_handler(connection):
    ws = await _resolve_ws(connection)
    try:
        async for text in ws:
            msg = json.loads(text)
            if msg.get("op") == "subscribe":
                # If client sends resume_seq include it in ack to show it was received
                ack = {"type": "subscribed", "payload": msg}
                await ws.send(json.dumps(ack))
                # Emit ticks with increasing seqs for the given symbol
                sym = msg.get("symbol")
                for i in range(1, 5):
                    await asyncio.sleep(0.02)
                    await ws.send(json.dumps({"type": "tick", "symbol": sym, "seq": i, "price": 100 + i}))
            else:
                await ws.send(json.dumps({"type": "echo", "payload": msg}))
    except websockets.ConnectionClosed:
        return


async def test_fetcher_persists_and_forwards(tmp_path):
    # Use a disk-backed sqlite db for persistence between fetcher restarts
    dbpath = str(tmp_path / "seqs.db")
    store = SeqStore(dbpath)

    received = []

    async def inbound(msg):
        received.append(msg)

    server = await websockets.serve(mock_server_handler, "127.0.0.1", 9011)
    fetcher = DhanFetcher("ws://127.0.0.1:9011/ws", store, inbound_handler=inbound, ping_interval=1.0)

    # start fetcher and subscribe
    await fetcher.start()
    await fetcher.subscribe("tick:ABC", {"op": "subscribe", "channel": "ticks", "symbol": "ABC"})
    # give slightly more time for subscribe handshake + server messages (helps CI/Windows timing)
    await asyncio.sleep(0.4)
    await fetcher.stop()

    # should have received ticks seq 1..4
    ticks = [m for m in received if m.get("type") == "tick"]
    assert len(ticks) >= 4
    assert store.get_last_seq("tick:ABC") == 4

    # Clear received and restart fetcher to test resume: server will again emit 1..4,
    # but because we persist last_seq=4, fetcher should ignore <=4 (no new ticks).
    received.clear()
    fetcher2 = DhanFetcher("ws://127.0.0.1:9011/ws", store, inbound_handler=inbound, ping_interval=1.0)
    await fetcher2.start()
    # subscribe should include resume_seq automatically from store
    await fetcher2.subscribe("tick:ABC", {"op": "subscribe", "channel": "ticks", "symbol": "ABC"})
    await asyncio.sleep(0.4)
    await fetcher2.stop()
    server.close()
    await server.wait_closed()

    # no new ticks forwarded since seqs were <= persisted last_seq
    ticks2 = [m for m in received if m.get("type") == "tick"]
    assert len(ticks2) == 0
