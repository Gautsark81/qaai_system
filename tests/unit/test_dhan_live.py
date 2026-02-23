# tests/unit/test_dhan_live.py
import asyncio
import json
import pytest
import contextlib
from integrations.dhan_live import DhanLiveConnector

class DummyWS:
    """
    Minimal websocket-like object that supports async iteration and close.
    """
    def __init__(self, msgs, delay=0.001):
        self._msgs = msgs
        self._delay = delay
        self.closed = False

    def __aiter__(self):
        return self._iter()

    async def _iter(self):
        for m in self._msgs:
            await asyncio.sleep(self._delay)
            yield json.dumps(m)

    async def close(self):
        self.closed = True


@contextlib.asynccontextmanager
async def fake_connect(url, **kwargs):
    # Return an async context manager that yields DummyWS
    sample_msgs = [
        {"type": "Ticker Data", "security_id": 1333, "LTP": "992.80"},
        {"type": "Quote Data", "security_id": 1333, "LTP": "992.80", "volume": 100}
    ]
    ws = DummyWS(sample_msgs)
    try:
        yield ws
    finally:
        await ws.close()


@pytest.mark.asyncio
async def test_connector_receives_and_parses():
    # pass connect_callable explicitly
    conn = DhanLiveConnector(feed_url="wss://fake", api_key="x", connect_callable=fake_connect)
    await conn.start()
    # wait until messages ingested
    await asyncio.sleep(0.05)
    # check queue
    results = []
    while not conn.messages_queue.empty():
        results.append(await conn.messages_queue.get())
    await conn.stop()
    assert any(m.get("type") == "Ticker Data" for m in results)
    assert any(m.get("type") == "Quote Data" for m in results)
