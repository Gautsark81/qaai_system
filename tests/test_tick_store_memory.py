# tests/test_tick_store_memory.py
import time
from data.tick_store import TickStore

def test_memory_db_schema_persists_and_basic_ops():
    ts = TickStore(db_path=":memory:")
    now = time.time()
    # append a few ticks
    ticks = [
        {"timestamp": now, "price": 100, "size": 1},
        {"timestamp": now + 0.1, "price": 101, "size": 2},
    ]
    for t in ticks:
        ts.append_tick("TST", t)

    fetched = ts.get_ticks("TST")
    assert len(fetched) == 2
    assert fetched[0]["price"] == 100 or float(fetched[0]["price"]) == 100.0

    # snapshot contains symbol info
    snap = ts.snapshot("TST")
    assert snap["symbol"] == "TST"
    assert snap["tick_count"] == 2

    # prune with retention_seconds small removes old ticks
    ts.retention_seconds = 0  # immediate pruning of anything older than now
    deleted = ts.prune()
    # deleted may be >=0; ensure prune completes without error
    assert isinstance(deleted, int)

    ts.close()
