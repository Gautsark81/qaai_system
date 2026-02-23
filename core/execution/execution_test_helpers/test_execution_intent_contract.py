from dataclasses import FrozenInstanceError
import pytest

from core.execution.intent import ExecutionIntent


def test_execution_intent_is_immutable():
    intent = ExecutionIntent(
        symbol="RELIANCE",
        side="BUY",
        quantity=10,
        price=2500.0,
        venue="PAPER",
    )

    with pytest.raises(FrozenInstanceError):
        intent.price = 2600.0


def test_execution_intent_has_required_fields():
    intent = ExecutionIntent(
        symbol="RELIANCE",
        side="BUY",
        quantity=1,
        price=2500.0,
        venue="PAPER",
    )

    assert intent.symbol == "RELIANCE"
    assert intent.side == "BUY"
    assert intent.quantity == 1
    assert intent.price == 2500.0
    assert intent.venue == "PAPER"
