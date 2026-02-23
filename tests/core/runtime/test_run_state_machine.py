import pytest

from core.runtime.run_states import RunState, ALLOWED_TRANSITIONS


def test_illegal_state_transition_is_blocked():
    assert RunState.CREATED not in ALLOWED_TRANSITIONS[RunState.COMPLETED]


def test_valid_state_transition_allowed():
    assert RunState.ACTIVE in ALLOWED_TRANSITIONS[RunState.CREATED]
