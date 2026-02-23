from modules.strategy_lifecycle.store import StrategyLifecycleStore
from modules.strategy_lifecycle.evaluator import StrategyLifecycleEvaluator
from modules.strategy_lifecycle.orchestrator import StrategyLifecycleOrchestrator
from modules.strategy_lifecycle.states import StrategyState


def test_orchestrator_success_path():
    store = StrategyLifecycleStore()
    orch = StrategyLifecycleOrchestrator(store, StrategyLifecycleEvaluator())
    orch.on_success("s1")
    assert store.get_state("s1") == StrategyState.ACTIVE
