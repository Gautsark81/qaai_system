# path suggestion: tests/test_dhan_safe_client_basic.py
import pytest

from qaai_system.broker.dhan_safe_client import (
    DhanSafeClient,
    DhanSafeConfig,
    BrokerOrderResult,
)


class DummyRawDhan:
    """Fake Dhan client to test DhanSafeClient behaviour."""

    def __init__(self):
        self.place_calls = []
        self.should_fail_first = False

    def place_order(self, **kwargs):
        self.place_calls.append(kwargs)
        if self.should_fail_first and len(self.place_calls) == 1:
            raise RuntimeError("Transient network error")
        return {
            "dhan_order_id": f"DO_{len(self.place_calls)}",
            "order_status": "SUCCESS",
        }


def test_place_order_idempotency_and_retry():
    cfg = DhanSafeConfig(client_id="x", access_token="y", max_retries=2)
    dummy = DummyRawDhan()
    dummy.should_fail_first = True

    safe = DhanSafeClient(config=cfg, raw_client=dummy)

    # First call should retry internally and succeed
    res1: BrokerOrderResult = safe.place_order(
        client_order_id="cli-1",
        symbol="NIFTY24FEBFUT",
        side="BUY",
        quantity=50,
        order_type="MARKET",
        product_type="INTRADAY",
    )

    assert res1.order_id.startswith("DO_")
    assert len(dummy.place_calls) == 2  # first failed, second succeeded

    # Second call with same client_order_id should be idempotent (no extra API hit)
    res2: BrokerOrderResult = safe.place_order(
        client_order_id="cli-1",
        symbol="NIFTY24FEBFUT",
        side="BUY",
        quantity=50,
        order_type="MARKET",
        product_type="INTRADAY",
    )

    assert res2.order_id == res1.order_id
    assert len(dummy.place_calls) == 2  # still only two raw calls
