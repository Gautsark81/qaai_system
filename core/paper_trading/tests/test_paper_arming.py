import pytest

from core.paper_trading.engine import PaperTradingEngine
from core.paper_trading.invariants import PaperTradingInvariantViolation


def test_paper_trading_not_armed_by_default():
    engine = PaperTradingEngine()
    assert engine.is_armed is False


def test_execution_blocked_when_not_armed():
    engine = PaperTradingEngine()

    with pytest.raises(PaperTradingInvariantViolation):
        engine.execute_order(
            symbol="RELIANCE",
            side="BUY",
            quantity=10,
            price=2500.0,
        )


def test_execution_allowed_when_armed():
    engine = PaperTradingEngine(armed=True)

    fill = engine.execute_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=10,
        price=2500.0,
    )

    assert fill is not None
