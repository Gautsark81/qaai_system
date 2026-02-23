# tests/execution/test_broker_signatures.py

import inspect
import pytest


EXPECTED_SIGNATURE = [
    "symbol",
    "side",
    "qty",
    "order_type",
    "price",
    "product_type",
    "tag",
]


def assert_signature(func, expected_params):
    sig = inspect.signature(func)
    actual = list(sig.parameters.keys())

    assert actual == expected_params, (
        f"Broker signature mismatch.\n"
        f"Expected: {expected_params}\n"
        f"Actual:   {actual}"
    )


# ---------------------------------------------------------
# Mock broker examples (replace with real brokers)
# ---------------------------------------------------------

class MockPaperBroker:
    def place_order(
        self,
        symbol,
        side,
        qty,
        order_type,
        price,
        product_type,
        tag=None,
    ):
        return {"status": "ok"}


class MockLiveBroker:
    def place_order(
        self,
        symbol,
        side,
        qty,
        order_type,
        price,
        product_type,
        tag=None,
    ):
        return {"order_id": "LIVE123"}


# ---------------------------------------------------------
# TESTS
# ---------------------------------------------------------

def test_paper_broker_signature():
    broker = MockPaperBroker()
    assert_signature(broker.place_order, EXPECTED_SIGNATURE)


def test_live_broker_signature():
    broker = MockLiveBroker()
    assert_signature(broker.place_order, EXPECTED_SIGNATURE)
