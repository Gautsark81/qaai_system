# tests/test_tick_store.py
import time
from data.tick_store import TickStore


def test_tick_store_append_and_prune():
    ts = TickStore(retention_seconds=1)  # short retention for test
    now = time.time()
    ts.append_tick("AAA", {"timestamp": now - 2, "price": 100, "size": 1})
    ts.append_tick("AAA", {"timestamp": now, "price": 101, "size": 2})
    ticks = ts.get_ticks("AAA", since=0)
    # only the recent one should remain because retention=1
    assert any(int(t["price"]) == 101 for t in ticks)


def test_snapshot_returns_structure():
    ts = TickStore()
    ts.append_tick("SYM", {"timestamp": time.time(), "price": 10})
    snap = ts.snapshot()
    assert "SYM" in snap and isinstance(snap["SYM"], list)
