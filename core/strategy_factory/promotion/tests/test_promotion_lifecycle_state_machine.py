import pytest
from datetime import datetime, timezone

from core.strategy_factory.promotion.lifecycle import (
    PromotionLifecycleState,
    PromotionLifecycleTransition,
    PromotionLifecycleMachine,
)
from core.strategy_factory.promotion.contracts import PromotionDecision


def _decision(promoted: bool):
    return PromotionDecision(
        strategy_dna="S1",
        promoted=promoted,
        sizing_fraction=0.2 if promoted else 0.0,
        reasons=["ok"] if promoted else ["blocked"],
        decided_at=datetime.now(tz=timezone.utc),
    )


# ------------------------------------------------------------------
# Initial State
# ------------------------------------------------------------------

def test_initial_state_is_candidate():
    machine = PromotionLifecycleMachine(strategy_dna="S1")
    assert machine.state == PromotionLifecycleState.CANDIDATE


# ------------------------------------------------------------------
# Valid Transitions
# ------------------------------------------------------------------

def test_candidate_to_approved_when_promoted():
    machine = PromotionLifecycleMachine(strategy_dna="S1")

    machine.apply_decision(_decision(promoted=True))

    assert machine.state == PromotionLifecycleState.APPROVED


def test_candidate_to_rejected_when_blocked():
    machine = PromotionLifecycleMachine(strategy_dna="S1")

    machine.apply_decision(_decision(promoted=False))

    assert machine.state == PromotionLifecycleState.REJECTED


# ------------------------------------------------------------------
# Illegal Transitions
# ------------------------------------------------------------------

def test_rejected_cannot_transition_to_approved():
    machine = PromotionLifecycleMachine(strategy_dna="S1")
    machine.apply_decision(_decision(promoted=False))

    with pytest.raises(RuntimeError):
        machine.apply_decision(_decision(promoted=True))


def test_approved_cannot_be_reapplied():
    machine = PromotionLifecycleMachine(strategy_dna="S1")
    machine.apply_decision(_decision(promoted=True))

    with pytest.raises(RuntimeError):
        machine.apply_decision(_decision(promoted=True))


# ------------------------------------------------------------------
# Terminal State Guarantees
# ------------------------------------------------------------------

def test_terminal_states_are_final():
    for terminal in (
        PromotionLifecycleState.APPROVED,
        PromotionLifecycleState.REJECTED,
    ):
        machine = PromotionLifecycleMachine(strategy_dna="S1")
        machine._state = terminal  # internal test-only access

        with pytest.raises(RuntimeError):
            machine.apply_decision(_decision(promoted=True))


# ------------------------------------------------------------------
# Audit / Trace
# ------------------------------------------------------------------

def test_transition_history_is_recorded():
    machine = PromotionLifecycleMachine(strategy_dna="S1")
    machine.apply_decision(_decision(promoted=True))

    history = machine.history()

    assert len(history) == 1
    assert history[0].from_state == PromotionLifecycleState.CANDIDATE
    assert history[0].to_state == PromotionLifecycleState.APPROVED
    assert isinstance(history[0].timestamp, datetime)


# ------------------------------------------------------------------
# Immutability
# ------------------------------------------------------------------

def test_transition_records_are_immutable():
    machine = PromotionLifecycleMachine(strategy_dna="S1")
    machine.apply_decision(_decision(promoted=True))

    transition = machine.history()[0]

    with pytest.raises(Exception):
        transition.to_state = PromotionLifecycleState.REJECTED
