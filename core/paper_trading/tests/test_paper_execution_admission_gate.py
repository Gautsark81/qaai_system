import pytest

from core.paper_trading.admission import (
    PaperExecutionAdmissionGate,
    PaperExecutionAdmissionViolation,
)
from core.paper_trading.invariants import PaperCapitalDecision, PaperAllocation
from core.operations.arming import ExecutionArming, SystemArmingState
from core.capital.allocator_v3.contracts import CapitalDecisionStatus


def _valid_decision():
    return PaperCapitalDecision(
        allocations={
            "dna-1": PaperAllocation(allocated_fraction=0.5)
        },
        decisions={},
        total_allocated=0.5,
        status=CapitalDecisionStatus.APPROVED,
    )


# ------------------------------------------------------------------
# Authority
# ------------------------------------------------------------------

def test_execution_blocked_when_system_not_armed():
    arming = ExecutionArming(state=SystemArmingState.DISARMED)
    gate = PaperExecutionAdmissionGate(arming=arming)

    with pytest.raises(PaperExecutionAdmissionViolation):
        gate.admit(
            dna="dna-1",
            capital_decision=_valid_decision(),
        )


def test_execution_allowed_when_system_armed():
    arming = ExecutionArming(state=SystemArmingState.ARMED)
    gate = PaperExecutionAdmissionGate(arming=arming)

    gate.admit(
        dna="dna-1",
        capital_decision=_valid_decision(),
    )


# ------------------------------------------------------------------
# Capital
# ------------------------------------------------------------------

def test_execution_blocked_when_no_capital_decision():
    arming = ExecutionArming(state=SystemArmingState.ARMED)
    gate = PaperExecutionAdmissionGate(arming=arming)

    with pytest.raises(PaperExecutionAdmissionViolation):
        gate.admit(
            dna="dna-1",
            capital_decision=None,
        )


def test_execution_blocked_when_zero_allocation():
    arming = ExecutionArming(state=SystemArmingState.ARMED)
    gate = PaperExecutionAdmissionGate(arming=arming)

    decision = PaperCapitalDecision(
        allocations={"dna-1": PaperAllocation(allocated_fraction=0.0)},
        decisions={},
        total_allocated=0.0,
        status=CapitalDecisionStatus.APPROVED,
    )

    with pytest.raises(PaperExecutionAdmissionViolation):
        gate.admit(
            dna="dna-1",
            capital_decision=decision,
        )


# ------------------------------------------------------------------
# Determinism & Purity
# ------------------------------------------------------------------

def test_admission_is_deterministic():
    arming = ExecutionArming(state=SystemArmingState.DISARMED)
    gate = PaperExecutionAdmissionGate(arming=arming)

    for _ in range(3):
        with pytest.raises(PaperExecutionAdmissionViolation):
            gate.admit(
                dna="dna-1",
                capital_decision=_valid_decision(),
            )


def test_admission_has_no_side_effects():
    arming = ExecutionArming(state=SystemArmingState.DISARMED)
    gate = PaperExecutionAdmissionGate(arming=arming)

    original_state = arming.state

    with pytest.raises(PaperExecutionAdmissionViolation):
        gate.admit(
            dna="dna-1",
            capital_decision=_valid_decision(),
        )

    assert arming.state == original_state
