from modules.strategy_lifecycle.store import StrategyLifecycleStore
from modules.strategy_lifecycle.evaluator import StrategyLifecycleEvaluator
from modules.strategy_lifecycle.states import StrategyState


class StrategyLifecycleOrchestrator:
    """
    Phase 9 lifecycle coordinator.

    No strategy imports.
    No execution imports.
    """

    def __init__(
        self,
        store: StrategyLifecycleStore,
        evaluator: StrategyLifecycleEvaluator,
    ):
        self.store = store
        self.evaluator = evaluator

    def on_success(self, strategy_id: str) -> None:
        self.store.set_state(
            strategy_id,
            self.evaluator.evaluate_on_success(),
        )

    def on_failure(self, strategy_id: str, failure_count: int) -> None:
        self.store.set_state(
            strategy_id,
            self.evaluator.evaluate_on_failure(failure_count),
        )

    def can_execute(self, strategy_id: str) -> bool:
        return self.store.get_state(strategy_id) == StrategyState.ACTIVE
