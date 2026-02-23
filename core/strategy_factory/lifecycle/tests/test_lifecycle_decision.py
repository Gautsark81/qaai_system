import pytest

from core.strategy_factory.lifecycle.contracts import StrategyLifecycleState
from core.strategy_factory.lifecycle.decision import decide_lifecycle_transition


def test_valid_transition_returns_new_state():
    new_state = decide_lifecycle_transition(
        current=StrategyLifecycleState.RESEARCH,
        requested=StrategyLifecycleState.BACKTESTED,
    )
    assert new_state == StrategyLifecycleState.BACKTESTED


def test_invalid_transition_raises():
    with pytest.raises(ValueError):
        decide_lifecycle_transition(
            current=StrategyLifecycleState.RESEARCH,
            requested=StrategyLifecycleState.LIVE,
        )


def test_terminal_state_cannot_transition():
    with pytest.raises(ValueError):
        decide_lifecycle_transition(
            current=StrategyLifecycleState.RETIRED,
            requested=StrategyLifecycleState.PAPER,
        )


def test_self_transition_forbidden():
    with pytest.raises(ValueError):
        decide_lifecycle_transition(
            current=StrategyLifecycleState.LIVE,
            requested=StrategyLifecycleState.LIVE,
        )
