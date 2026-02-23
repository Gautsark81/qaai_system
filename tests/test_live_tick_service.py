# tests/test_live_tick_service.py
import asyncio
import time
import pytest
from types import SimpleNamespace
from services.live_tick_service import LiveTickService, normalize_packet

class DummyTickStore:
    def __init__(self):
        self._ticks = []
    def append_tick(self, symbol, tick):
        self._ticks.append((symbol, tick))
    def get_all(self):
        return self._ticks

class DummyFeed:
    def __init__(self, packets):
        self._packets = list(packets)
    def get_data(self):
        if not self._packets:
            return None
        return self._packets.pop(0)
    def run_forever(self):
        # Not used in test
        pass
    def stop(self):
        pass

@pytest.mark.asyncio
async def test_live_tick_service_normalize_and_append(monkeypatch):
    now = time.time()
    pkt = {"type":"Ticker Data","exchange_segment":1,"security_id":11915,"LTP":"22.71","LTT":"12:00:00"}
    # patch MarketFeed and DhanContext usage by injecting feed into LiveTickService._feed and running _publish_tick directly
    ts = DummyTickStore()
    svc = LiveTickService(dhan_context=None, instruments=[], tick_store=ts, redis_client=None)

    tick = normalize_packet(pkt)
    assert tick is not None
    svc._publish_tick(tick)
    assert len(ts.get_all()) == 1
    sym, stored = ts.get_all()[0]
    assert sym == tick["symbol"]
