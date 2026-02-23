from domain.strategy_lifecycle.lifecycle_state import StrategyLifecycleState


def test_lifecycle_states_exist():
    assert StrategyLifecycleState.LIVE.value == "LIVE"
