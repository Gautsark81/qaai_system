# tests/test_async_order_manager.py
import asyncio
import time
import pytest
from clients.dhan_safe_client import MockDhanSafeClient
from clients.order_manager import OrderManager
from clients.async_order_manager import AsyncOrderManager

@pytest.mark.asyncio
async def test_async_place_order_nonblocking_event_loop():
    client = MockDhanSafeClient()
    om = OrderManager(client)
    aom = AsyncOrderManager(om)
    start = time.time()
    # schedule several place_order coroutines concurrently
    coros = [aom.place_order("TST", "BUY", qty=1, price=10.0, idempotency_key=f"k-{i}") for i in range(6)]
    res = await asyncio.gather(*coros)
    assert len(res) == 6
    # ensure event loop was not blocked (operations completed quickly)
    assert time.time() - start < 1.0
    # idempotency ensures repeated key returns same order
    r1 = await aom.place_order("TST", "BUY", qty=1, price=10.0, idempotency_key="k-0")
    assert r1["order_id"] == res[0]["order_id"]
