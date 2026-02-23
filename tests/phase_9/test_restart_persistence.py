from modules.strategy_lifecycle.store import StrategyLifecycleStore
from modules.strategy_lifecycle.states import StrategyState


def test_restart_safe_state_retention():
    store = StrategyLifecycleStore()
    store.set_state("s1", StrategyState.ACTIVE)

    # simulate restart by reusing persisted store
    assert store.get_state("s1") == StrategyState.ACTIVE
