import pytest
from unittest.mock import MagicMock

from core.paper_trading.engine import PaperTradingEngine
from core.paper_trading.admission import PaperExecutionAdmissionGate
from core.paper_trading.invariants import PaperTradingInvariantViolation
from core.execution.arming import ExecutionArming, SystemArmingState


def test_engine_calls_admission_gate_before_execution():
    """
    Engine MUST delegate execution admission to PaperExecutionAdmissionGate.
    """

    arming = ExecutionArming(state=SystemArmingState.ARMED)

    admission_gate = PaperExecutionAdmissionGate(arming=arming)
    admission_gate.admit = MagicMock(return_value=None)

    engine = PaperTradingEngine(admission_gate=admission_gate)

    engine.execute_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=1,
        price=2500.0,
    )

    admission_gate.admit.assert_called_once_with(
        symbol="RELIANCE",
        side="BUY",
        quantity=1,
        price=2500.0,
    )


def test_engine_blocks_execution_if_admission_gate_raises():
    """
    Engine MUST propagate admission failures verbatim.
    """

    arming = ExecutionArming(state=SystemArmingState.DISARMED)

    admission_gate = PaperExecutionAdmissionGate(arming=arming)

    engine = PaperTradingEngine(admission_gate=admission_gate)

    with pytest.raises(PaperTradingInvariantViolation):
        engine.execute_order(
            symbol="RELIANCE",
            side="BUY",
            quantity=1,
            price=2500.0,
        )


def test_engine_does_not_call_broker_when_admission_fails():
    """
    Admission failure MUST short-circuit execution.
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

    with pytest.raises(PaperTradingInvariantViolation):
        engine.execute_order(
            symbol="RELIANCE",
            side="BUY",
            quantity=1,
            price=2500.0,
        )

    broker.place_order.assert_not_called()
    ledger.record.assert_not_called()
