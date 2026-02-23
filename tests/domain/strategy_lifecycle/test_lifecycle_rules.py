from domain.strategy_lifecycle.lifecycle_rules import LifecycleRules
from domain.strategy_lifecycle.lifecycle_state import StrategyLifecycleState


def test_valid_transition():
    assert LifecycleRules.can_transition(
        StrategyLifecycleState.PAPER,
        StrategyLifecycleState.LIVE_CANDIDATE,
    )


def test_invalid_transition():
    assert not LifecycleRules.can_transition(
        StrategyLifecycleState.CREATED,
        StrategyLifecycleState.LIVE,
    )
