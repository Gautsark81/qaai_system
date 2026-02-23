# tests/test_ohlcv_integration.py
from data.tick_store import TickStore
from data.ohlcv import ticks_to_1min_ohlcv
import time


def test_tick_to_ohlcv_simple():
    ts = TickStore()
    now = time.time()
    ticks = [
        {"timestamp": now, "price": 100, "size": 1},
        {"timestamp": now, "price": 101, "size": 2},
        {"timestamp": now, "price": 99, "size": 1},
    ]
    for t in ticks:
        ts.append_tick("TST", t)
    got = ts.get_ticks("TST")
    o = ticks_to_1min_ohlcv(got)
    assert (
        o["open"] == 100
        and o["high"] == 101
        and o["low"] == 99
        and o["close"] == 99
        and o["volume"] == 4
    )
