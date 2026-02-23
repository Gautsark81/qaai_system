from unittest.mock import MagicMock
import pytest

from core.paper_trading.engine import PaperTradingEngine
from core.paper_trading.invariants import PaperTradingInvariantViolation
from core.paper_trading.admission import PaperExecutionAdmissionGate
from core.execution.intent import ExecutionIntent
from core.operations.arming import ExecutionArming, SystemArmingState

# ---------------------------------------------------------------------
# Phase 14.4 — ExecutionIntent consumption (Paper)
# ---------------------------------------------------------------------


def _intent():
    return ExecutionIntent(
        symbol="RELIANCE",
        side="BUY",
        quantity=10,
        price=2500.0,
        venue="PAPER",
    )


def test_engine_accepts_execution_intent_when_armed():
    """
    Engine MUST accept ExecutionIntent as execution payload
    when system is armed.
    """

    arming = ExecutionArming(state=SystemArmingState.ARMED)
    admission_gate = PaperExecutionAdmissionGate(arming=arming)

    engine = PaperTradingEngine(admission_gate=admission_gate)

    intent = _intent()

    result = engine.execute_intent(intent)

    assert result["symbol"] == intent.symbol
    assert result["side"] == intent.side
    assert result["quantity"] == intent.quantity
    assert result["price"] == intent.price
    assert result["status"] == "FILLED"


def test_engine_blocks_execution_intent_when_disarmed():
    """
    Admission failure via ExecutionIntent MUST raise invariant violation.
    """

    arming = ExecutionArming(state=SystemArmingState.DISARMED)
    admission_gate = PaperExecutionAdmissionGate(arming=arming)

    engine = PaperTradingEngine(admission_gate=admission_gate)

    intent = _intent()

    with pytest.raises(PaperTradingInvariantViolation):
        engine.execute_intent(intent)


def test_engine_delegates_execution_intent_to_admission_gate():
    """
    Engine MUST delegate ExecutionIntent to admission gate verbatim.
    """

    arming = ExecutionArming(state=SystemArmingState.ARMED)
    admission_gate = PaperExecutionAdmissionGate(arming=arming)
    admission_gate.admit = MagicMock(return_value=None)

    engine = PaperTradingEngine(admission_gate=admission_gate)

    intent = _intent()
    engine.execute_intent(intent)

    admission_gate.admit.assert_called_once_with(intent)


def test_engine_does_not_execute_when_admission_rejects_intent():
    """
    Admission rejection MUST short-circuit execution.
    No broker / ledger interaction is allowed.
    """

    arming = ExecutionArming(state=SystemArmingState.DISARMED)
    admission_gate = PaperExecutionAdmissionGate(arming=arming)

    broker = MagicMock()
    ledger = MagicMock()

    engine = PaperTradingEngine(
        admission_gate=admission_gate,
        broker=broker,
        ledger=ledger,
    )

    intent = _intent()

    with pytest.raises(PaperTradingInvariantViolation):
        engine.execute_intent(intent)

    broker.assert_not_called()
    ledger.assert_not_called()


def test_execution_intent_consumption_preserves_parity_with_execute_order():
    """
    ExecutionIntent execution MUST be semantically identical
    to legacy execute_order().
    """

    arming = ExecutionArming(state=SystemArmingState.ARMED)
    admission_gate = PaperExecutionAdmissionGate(arming=arming)

    engine = PaperTradingEngine(admission_gate=admission_gate)

    intent = _intent()

    result_intent = engine.execute_intent(intent)

    result_legacy = engine.execute_order(
        symbol=intent.symbol,
        side=intent.side,
        quantity=intent.quantity,
        price=intent.price,
    )

    assert result_intent == result_legacy
