import pytest

from core.paper_trading.engine import PaperTradingEngine
from core.paper_trading.invariants import (
    PaperTradingInvariantViolation,
    PaperExecutionInvariantGuard,
)
from core.operations.arming import ExecutionArming, SystemArmingState


def test_paper_execution_blocked_when_system_not_armed():
    """
    Paper execution MUST be blocked when the system is not armed.

    This must raise a paper-scoped invariant violation,
    NOT a runtime or execution exception.
    """
    arming = ExecutionArming(state=SystemArmingState.DISARMED)
    guard = PaperExecutionInvariantGuard(arming=arming)

    engine = PaperTradingEngine(invariant_guard=guard)

    with pytest.raises(PaperTradingInvariantViolation):
        engine.execute_order(
            symbol="RELIANCE",
            side="BUY",
            quantity=10,
            price=2500.0,
        )


def test_paper_execution_allowed_when_system_armed():
    """
    When system is armed, paper execution is permitted.

    No invariant violation should be raised.
    """
    arming = ExecutionArming(state=SystemArmingState.ARMED)
    guard = PaperExecutionInvariantGuard(arming=arming)

    engine = PaperTradingEngine(invariant_guard=guard)

    result = engine.execute_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=10,
        price=2500.0,
    )

    assert result is not None


def test_paper_invariant_is_deterministic():
    """
    Invariant violations MUST be deterministic and replay-safe.
    """
    arming = ExecutionArming(state=SystemArmingState.DISARMED)
    guard = PaperExecutionInvariantGuard(arming=arming)

    engine = PaperTradingEngine(invariant_guard=guard)

    with pytest.raises(PaperTradingInvariantViolation) as exc1:
        engine.execute_order(
            symbol="INFY",
            side="SELL",
            quantity=5,
            price=1500.0,
        )

    with pytest.raises(PaperTradingInvariantViolation) as exc2:
        engine.execute_order(
            symbol="INFY",
            side="SELL",
            quantity=5,
            price=1500.0,
        )

    assert str(exc1.value) == str(exc2.value)


def test_paper_invariant_has_no_side_effects():
    """
    Invariant enforcement MUST NOT mutate arming state,
    engine state, or any external state.
    """
    arming = ExecutionArming(state=SystemArmingState.DISARMED)
    guard = PaperExecutionInvariantGuard(arming=arming)

    engine = PaperTradingEngine(invariant_guard=guard)

    with pytest.raises(PaperTradingInvariantViolation):
        engine.execute_order(
            symbol="TCS",
            side="BUY",
            quantity=1,
            price=3800.0,
        )

    # Arming state must remain unchanged
    assert arming.state == SystemArmingState.DISARMED
