from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_context import RegimeContext
from core.context.context_wiring import StrategyContextProvider
from core.strategy.context_consumer import ContextAwareStrategy


class DummyStrategy(ContextAwareStrategy):
    """
    A strategy that emits fixed orders.
    Context must not affect execution-relevant fields.
    """

    def generate_orders(self, market_data):
        return [
            {"symbol": "NIFTY", "side": "buy", "quantity": 100, "price": 100.0}
        ]


def _setup_context():
    memory = RegimeMemory()
    memory.append(
        symbol="NIFTY",
        regime=MarketRegime.RANGING,
        confidence=0.7,
        detector_id="test",
        evidence={},
    )

    base = RegimeContext(memory)
    return StrategyContextProvider(base)


def _strip_context(orders):
    """
    Remove context metadata from orders for behavioral comparison.
    """
    return [
        {k: v for k, v in o.items() if k != "context"}
        for o in orders
    ]


def test_strategy_can_receive_context_snapshot():
    provider = _setup_context()
    strategy = DummyStrategy(context_provider=provider)

    snap = strategy.context_snapshot("NIFTY")

    assert snap["current_regime"] == MarketRegime.RANGING
    assert "stability_score" in snap


def test_strategy_orders_unchanged_with_context():
    """
    Context annotation is allowed, but execution-relevant
    order fields must remain identical.
    """
    provider = _setup_context()
    strategy = DummyStrategy(context_provider=provider)

    orders_with_context = strategy.generate_orders({})

    strategy_no_context = DummyStrategy(context_provider=None)
    orders_without_context = strategy_no_context.generate_orders({})

    assert _strip_context(orders_with_context) == orders_without_context


def test_strategy_cannot_mutate_context():
    provider = _setup_context()
    strategy = DummyStrategy(context_provider=provider)

    snap = strategy.context_snapshot("NIFTY")

    try:
        snap["current_regime"] = MarketRegime.TRENDING
        mutated = True
    except Exception:
        mutated = False

    assert mutated is False


def test_strategy_without_context_is_supported():
    strategy = DummyStrategy(context_provider=None)

    snap = strategy.context_snapshot("NIFTY")

    assert snap is None
