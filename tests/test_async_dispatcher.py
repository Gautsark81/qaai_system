# tests/test_async_dispatcher.py
import time
import pytest
from data.dispatcher import AsyncDispatcher
from data.registry import StrategyRegistry
from data.strategy import StrategyContext
from data.tick_store import TickStore
from clients.dhan_safe_client import MockDhanSafeClient
# register example strategy
import examples.strategies.simple_mean_reversion  # noqa: F401

def test_dispatcher_routing_and_ordering():
    ts = TickStore(db_path=":memory:")
    client = MockDhanSafeClient()
    reg = StrategyRegistry()
    # create instance (id must match what we use for mapping)
    ctx = StrategyContext(tick_store=ts, order_client=client, config={"name": "smr", "window": 3, "threshold": 0.01})
    inst = reg.create("simple_mean_reversion", ctx, instance_id="smr-1")

    disp = AsyncDispatcher(registry=reg, max_queue_size=128)
    disp.start()

    # map symbol to instance
    disp.map_symbol_to_instance("SMB", "smr-1", strategy_obj=inst)

    # submit ticks in order
    now = time.time()
    ticks = [
        {"symbol": "SMB", "timestamp": now, "price": 100.0, "size": 1},
        {"symbol": "SMB", "timestamp": now + 0.001, "price": 99.0, "size": 1},
        {"symbol": "SMB", "timestamp": now + 0.002, "price": 101.5, "size": 1},
    ]
    for t in ticks:
        ok = disp.submit_tick("SMB", t)
        assert ok

    # wait a little for processing
    time.sleep(0.5)

    # ensure dispatcher handled ticks (no exceptions, some orders may have been placed by strategy)
    # check that client's orders are present or at least that tick_count in TickStore is correct
    fetched = ts.get_ticks("SMB")
    assert len(fetched) == 3

    # cleanup
    disp.stop()
    ts.close()

def test_dispatcher_missing_mapping_drops():
    ts = TickStore(db_path=":memory:")
    client = MockDhanSafeClient()
    reg = StrategyRegistry()
    disp = AsyncDispatcher(registry=reg)
    disp.start()

    # submit without mapping
    ok = disp.submit_tick("NOPE", {"symbol": "NOPE", "timestamp": time.time(), "price": 1.0})
    assert ok is False

    disp.stop()
    ts.close()
