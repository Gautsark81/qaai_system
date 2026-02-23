from datetime import datetime
from unittest.mock import Mock

from modules.execution.execution_gate import ExecutionGate
from modules.strategies.intent import StrategyIntent


def _make_intent(side: str) -> StrategyIntent:
    """
    Construct a fully valid StrategyIntent
    according to the locked Phase-9 contract.
    """
    return StrategyIntent(
        strategy_id="strategy_1",
        side=side,
        symbol="TEST",
        confidence=0.75,
        features_used=["f1", "f2"],
        timestamp=datetime.utcnow(),
    )


def test_intent_blocked_when_lifecycle_disallows():
    lifecycle = Mock()
    lifecycle.can_execute.return_value = False

    execution = Mock()

    gate = ExecutionGate(
        lifecycle_orchestrator=lifecycle,
        execution_orchestrator=execution,
    )

    intent = _make_intent("BUY")

    result = gate.handle_intent(
        strategy_id="strategy_1",
        intent=intent,
        order_id="order_1",
        order_payload={"symbol": "TEST"},
    )

    assert result is False
    execution.submit_order.assert_not_called()


def test_intent_executed_when_lifecycle_allows():
    lifecycle = Mock()
    lifecycle.can_execute.return_value = True

    execution = Mock()

    gate = ExecutionGate(
        lifecycle_orchestrator=lifecycle,
        execution_orchestrator=execution,
    )

    intent = _make_intent("SELL")

    result = gate.handle_intent(
        strategy_id="strategy_1",
        intent=intent,
        order_id="order_2",
        order_payload={"symbol": "TEST"},
    )

    assert result is True
    execution.submit_order.assert_called_once_with(
        order_id="order_2",
        order_payload={"symbol": "TEST"},
    )


def test_none_intent_is_ignored():
    lifecycle = Mock()
    execution = Mock()

    gate = ExecutionGate(
        lifecycle_orchestrator=lifecycle,
        execution_orchestrator=execution,
    )

    result = gate.handle_intent(
        strategy_id="strategy_1",
        intent=None,
        order_id="order_3",
        order_payload={"symbol": "TEST"},
    )

    assert result is False
    execution.submit_order.assert_not_called()
