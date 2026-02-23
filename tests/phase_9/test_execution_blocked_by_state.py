from modules.strategy_lifecycle.store import StrategyLifecycleStore
from modules.strategy_lifecycle.states import StrategyState
from modules.strategy_lifecycle.orchestrator import StrategyLifecycleOrchestrator
from modules.strategy_lifecycle.evaluator import StrategyLifecycleEvaluator


def test_execution_blocked_when_not_active():
    store = StrategyLifecycleStore()
    orch = StrategyLifecycleOrchestrator(store, StrategyLifecycleEvaluator())

    store.set_state("s1", StrategyState.DISABLED)
    assert orch.can_execute("s1") is False
