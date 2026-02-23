from modules.strategy_lifecycle.store import StrategyLifecycleStore
from modules.strategy_lifecycle.states import StrategyState


def test_default_state_is_init():
    store = StrategyLifecycleStore()
    assert store.get_state("s1") == StrategyState.INIT


def test_state_persistence():
    store = StrategyLifecycleStore()
    store.set_state("s1", StrategyState.ACTIVE)
    assert store.get_state("s1") == StrategyState.ACTIVE
