from modules.strategy_lifecycle.states import StrategyState


class StrategyLifecycleEvaluator:
    """
    Pure evaluator.

    No imports from strategies or execution.
    """

    def evaluate_on_success(self) -> StrategyState:
        return StrategyState.ACTIVE

    def evaluate_on_failure(self, failure_count: int) -> StrategyState:
        if failure_count >= 3:
            return StrategyState.DISABLED
        return StrategyState.FAILED
