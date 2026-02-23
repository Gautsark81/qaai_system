# tests/unit/test_router.py
import pytest
from unittest import mock

@pytest.fixture
def fake_client():
    from infra.dhan_client_sim import DhanClientSim
    return DhanClientSim(seed=42, default_latency_sec=0.0)

def test_router_places_order_and_forwards_ack(monkeypatch, fake_client):
    # adapt import to your router implementation path
    try:
        from execution import router
    except Exception:
        pytest.skip("router module not available; adapt test to your repo structure")

    # create a minimal fake router behavior if needed
    # monkeypatch router's client to our fake_client
    if hasattr(router, "client"):
        router.client = fake_client
    # If router exposes a place_order function:
    if hasattr(router, "place_order"):
        oid = router.place_order(symbol="NSE:ABC", qty=2, price=10.0, side="BUY")
        assert oid is not None
    else:
        pytest.skip("router.place_order not present; adapt test")
