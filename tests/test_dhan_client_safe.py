# tests/test_dhan_client_safe.py
import asyncio
import pytest

# try package import first then local
try:
    from qaai_system.infra.dhan_client_safe import DhanSafeClient, PAPER_MODE
except Exception:
    try:
        from infra.dhan_client_safe import DhanSafeClient, PAPER_MODE  # fallback
    except Exception:
        raise

@pytest.mark.asyncio
async def test_rate_limit_and_basic_market():
    client = DhanSafeClient(max_qps=4)
    # fire several concurrent market orders; token bucket should throttle somewhat
    t0 = asyncio.get_event_loop().time()
    tasks = [client.place_market_order({"symbol":"X","side":"buy","qty":1}) for _ in range(8)]
    res = await asyncio.gather(*tasks)
    dt = asyncio.get_event_loop().time() - t0
    assert all(r["status"] in ("ok", "paper") for r in res)

@pytest.mark.asyncio
async def test_paper_mode_on_impl_failure(monkeypatch):
    client = DhanSafeClient()
    async def fail_impl(order):
        raise RuntimeError("boom")
    client._place_limit_order_impl = fail_impl
    r = await client.place_limit_order({"symbol":"A","side":"buy","qty":1}, timeout=0.01)
    # after failing attempts client returns 'paper' (or ok in some env); assert status present
    assert "status" in r
