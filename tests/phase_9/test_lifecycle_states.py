from modules.strategy_lifecycle.states import StrategyState


def test_states_are_closed():
    assert StrategyState.ACTIVE.value == "ACTIVE"
    assert StrategyState.DISABLED.value == "DISABLED"
