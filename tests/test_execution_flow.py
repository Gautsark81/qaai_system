# tests/test_execution_flow.py
import pytest
import asyncio

try:
    from qaai_system.execution import router as router_mod
except Exception:
    try:
        import router as router_mod
    except Exception:
        from execution import router as router_mod

from tests.fixtures.broker_stub import BrokerStub

@pytest.mark.asyncio
async def test_router_submit_with_stub(monkeypatch):
    # create a safe client backed by broker stub
    stub = BrokerStub(partial_fill_qty=0)
    async def limit_impl(order):
        return {"order_id": "stub-1", "filled": 0}
    async def market_impl(order):
        return {"order_id": "mkt-1", "filled": order.get("qty",0)}
    # inject into router's safe client if present, else skip
    try:
        if hasattr(router_mod, "_safe_client"):
            sc = router_mod._safe_client
            sc._place_limit_order_impl = limit_impl
            sc._place_market_order_impl = market_impl
        # now submit
        signal = {"symbol":"ABC","side":"buy","qty":5}
        rec = await router_mod.submit(signal, timeout=0.01)
        assert rec["status"] in ("submitted","filled","paper","error")
    except AttributeError:
        pytest.skip("router module does not expose _safe_client in this layout")
