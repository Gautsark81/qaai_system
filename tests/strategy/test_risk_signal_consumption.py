import pytest

from core.regime.regime_memory import RegimeMemory
from core.regime.regime_types import MarketRegime
from core.regime.regime_context import RegimeContext
from core.context.context_wiring import StrategyContextProvider
from core.strategy.context_consumer import ContextAwareStrategy


# ---------------------------------------------------------------------
# Dummy strategy
# ---------------------------------------------------------------------

class DummyRiskAwareStrategy(ContextAwareStrategy):
    """
    Strategy that *observes* risk signals but must never
    alter execution behavior.
    """

    def generate_orders(self, market_data):
        # Explicitly read risk signals (allowed)
        snap = self.context_snapshot("NIFTY")
        if snap is not None:
            _ = snap.get("risk_signals")

        # Fixed output — must never change
        return [
            {
                "symbol": "NIFTY",
                "side": "buy",
                "quantity": 100,
                "price": 100.0,
            }
        ]


# ---------------------------------------------------------------------
# Test setup
# ---------------------------------------------------------------------

def _setup_context():
    memory = RegimeMemory()
    memory.append(
        symbol="NIFTY",
        regime=MarketRegime.TRENDING,
        confidence=0.8,
        detector_id="regime_detector_v1",
        evidence={},
    )
    base = RegimeContext(memory)
    return StrategyContextProvider(base)


# ---------------------------------------------------------------------
# Phase-6.3 — Strategy-Facing Risk Signal Consumption
# ---------------------------------------------------------------------

def test_strategy_can_read_risk_signals():
    """
    Strategy must be able to access risk signals.
    """
    provider = _setup_context()
    strategy = DummyRiskAwareStrategy(context_provider=provider)

    snap = strategy.context_snapshot("NIFTY")

    assert "risk_signals" in snap


def test_strategy_orders_unchanged_by_risk_signals():
    """
    Risk signals must not alter execution output.
    """
    provider = _setup_context()
    strategy = DummyRiskAwareStrategy(context_provider=provider)

    orders_with_risk = strategy.generate_orders({})

    strategy_no_context = DummyRiskAwareStrategy(context_provider=None)
    orders_without_risk = strategy_no_context.generate_orders({})

    assert orders_with_risk == orders_without_risk


def test_risk_signals_do_not_leak_into_orders():
    """
    Risk signals must never appear in orders.
    """
    provider = _setup_context()
    strategy = DummyRiskAwareStrategy(context_provider=provider)

    orders = strategy.generate_orders({})

    for order in orders:
        assert "risk_signals" not in order
        assert "risk_level" not in order
        assert "confidence" not in order


def test_strategy_cannot_mutate_risk_signals():
    """
    Risk signals must be immutable from strategy side.
    """
    provider = _setup_context()
    strategy = DummyRiskAwareStrategy(context_provider=provider)

    snap = strategy.context_snapshot("NIFTY")
    signals = snap["risk_signals"]

    with pytest.raises(TypeError):
        signals["risk_level"] = "HIGH"


def test_strategy_remains_functional_without_risk_signals():
    """
    Strategy must not depend on risk signals for execution.
    """
    strategy = DummyRiskAwareStrategy(context_provider=None)

    orders = strategy.generate_orders({})

    assert orders == [
        {
            "symbol": "NIFTY",
            "side": "buy",
            "quantity": 100,
            "price": 100.0,
        }
    ]
