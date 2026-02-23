import pytest
from core.strategy_factory.lifecycle.state_machine import (
    LifecycleState,
    validate_transition,
)
from core.strategy_factory.exceptions import IllegalLifecycleTransition


def test_valid_transition():
    validate_transition(LifecycleState.CREATED, LifecycleState.SCREENED)


def test_invalid_transition():
    with pytest.raises(IllegalLifecycleTransition):
        validate_transition(LifecycleState.CREATED, LifecycleState.LIVE)
