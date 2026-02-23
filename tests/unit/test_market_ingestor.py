import asyncio
import json
import contextlib
import pytest
from ingestion.market_ingestor import MarketIngestor
from integrations.dhan_live import DhanLiveConnector

# Reuse DummyWS style used earlier in other tests
class DummyWS:
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
    sample_msgs = [
        {"type": "Ticker Data", "security_id": 1333, "LTP": "992.80", "LTT": "11:02:23"},
        {"type": "Quote Data", "security_id": 1333, "LTP": "992.80", "volume": 100, "LTT": "11:02:24"},
        {"type": "Previous Close", "security_id": 1333, "prev_close": "1002.10"}
    ]
    ws = DummyWS(sample_msgs)
    try:
        yield ws
    finally:
        await ws.close()

@pytest.mark.asyncio
async def test_market_ingestor_normalizes_and_queues():
    out_q = asyncio.Queue()
    # provide the fake connect callable
    ingestor = MarketIngestor(
        feed_url="wss://fake",
        api_key="x",
        out_queue=out_q,
        connect_callable=fake_connect,
    )
    await ingestor.start()
    # allow messages to flow
    await asyncio.sleep(0.05)
    # gather ticks from the out queue
    ticks = []
    while not out_q.empty():
        ticks.append(await out_q.get())
    await ingestor.stop()

    # at least the 2 messages of types Ticker/Quote should be normalized
    types = [t["raw_type"] for t in ticks if "raw_type" in t]
    assert "Ticker Data" in types
    assert "Quote Data" in types
    # previous close should not be normalized
    assert all(t["raw_type"] != "Previous Close" for t in ticks if "raw_type" in t) or "Previous Close" not in types
