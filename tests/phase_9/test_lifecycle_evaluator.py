from modules.strategy_lifecycle.evaluator import StrategyLifecycleEvaluator
from modules.strategy_lifecycle.states import StrategyState


def test_success_promotes_active():
    ev = StrategyLifecycleEvaluator()
    assert ev.evaluate_on_success() == StrategyState.ACTIVE


def test_failure_threshold_disables():
    ev = StrategyLifecycleEvaluator()
    assert ev.evaluate_on_failure(3) == StrategyState.DISABLED
