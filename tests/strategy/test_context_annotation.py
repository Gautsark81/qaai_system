# tests/strategy/test_context_annotation.py

import pytest
from copy import deepcopy

from core.strategy.context_consumer import ContextAwareStrategy


class DummyContextProvider:
    def get(self, symbol: str):
        return {
            "symbol": symbol,
            "market_regime": "TRENDING",
            "confidence": 0.82,
        }


class DummyStrategy(ContextAwareStrategy):
    """
    Explicitly opts in to context annotation.

    This is REQUIRED under Phase-6 governance rules.
    """
    ATTACH_CONTEXT_TO_ORDERS = True

    def __init__(self, context_provider=None):
        super().__init__(context_provider=context_provider)

    def generate_orders(self, market_data):
        return [
            {
                "symbol": market_data["symbol"],
                "side": "buy",
                "quantity": 10,
                "price": 100.0,
            }
        ]


def test_context_is_attached_to_order_metadata():
    strategy = DummyStrategy(context_provider=DummyContextProvider())

    orders = strategy.generate_orders({"symbol": "NIFTY"})
    order = orders[0]

    assert "context" in order
    assert order["context"]["market_regime"] == "TRENDING"


def test_order_fields_are_unchanged_except_context():
    strategy = DummyStrategy(context_provider=DummyContextProvider())

    orders = strategy.generate_orders({"symbol": "NIFTY"})
    annotated = orders[0]

    base = deepcopy(annotated)
    base.pop("context")

    assert base == {
        "symbol": "NIFTY",
        "side": "buy",
        "quantity": 10,
        "price": 100.0,
    }


def test_missing_context_provider_is_safe():
    """
    Even with opt-in enabled, missing provider must not break execution.
    """
    strategy = DummyStrategy(context_provider=None)

    orders = strategy.generate_orders({"symbol": "NIFTY"})
    order = orders[0]

    assert "context" not in order


def test_context_is_read_only():
    strategy = DummyStrategy(context_provider=DummyContextProvider())
    order = strategy.generate_orders({"symbol": "NIFTY"})[0]

    with pytest.raises(TypeError):
        order["context"]["confidence"] = 0.5
