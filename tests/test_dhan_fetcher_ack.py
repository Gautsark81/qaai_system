# tests/test_dhan_fetcher_ack.py
import asyncio
import json
import pytest
import websockets

from modules.dhan.fetcher import DhanFetcher, SeqStore

pytestmark = pytest.mark.asyncio

async def mock_server_handler_ack(connection):
    ws = connection if not isinstance(connection, tuple) else connection[0]
    try:
        async for text in ws:
            msg = json.loads(text)
            # On subscribe, send a tick BEFORE ack, then ack, then another tick
            if msg.get("op") == "subscribe":
                sym = msg.get("symbol")
                # tick before ack (should be dropped by fetcher when ACK mode enabled)
                await ws.send(json.dumps({"type": "tick", "symbol": sym, "seq": 1, "price": 100}))
                # small delay then send subscribed ack
                await asyncio.sleep(0.05)
                await ws.send(json.dumps({"type": "subscribed", "payload": {"symbol": sym, "channel": "ticks"}}))
                # then another tick (should be accepted)
                await asyncio.sleep(0.01)
                await ws.send(json.dumps({"type": "tick", "symbol": sym, "seq": 2, "price": 101}))
            else:
                await ws.send(json.dumps({"type": "echo", "payload": msg}))
    except websockets.ConnectionClosed:
        return

async def test_subscribe_ack_mode(tmp_path):
    dbpath = str(tmp_path / "seqs.db")
    store = SeqStore(dbpath)
    received = []

    async def inbound(msg):
        received.append(msg)

    server = await websockets.serve(mock_server_handler_ack, "127.0.0.1", 9022)
    # create fetcher with await_subscribe_ack True
    fetcher = DhanFetcher("ws://127.0.0.1:9022/ws", store, inbound_handler=inbound, await_subscribe_ack=True, subscribe_ack_timeout=0.5)
    await fetcher.start()
    await fetcher.subscribe("tick:ABC", {"op": "subscribe", "channel": "ticks", "symbol": "ABC"})
    # allow time for messages
    await asyncio.sleep(0.3)
    await fetcher.stop()
    server.close()
    await server.wait_closed()

    # verify that only the second tick (seq==2) is forwarded, seq==1 should be dropped
    ticks = [m for m in received if m.get("type") == "tick"]
    assert any(t.get("seq") == 2 for t in ticks)
    assert not any(t.get("seq") == 1 for t in ticks)
