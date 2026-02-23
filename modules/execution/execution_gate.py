# modules/execution/execution_gate.py

from typing import Optional

from modules.strategies.intent import StrategyIntent
from modules.strategy_lifecycle.orchestrator import StrategyLifecycleOrchestrator
from modules.execution.orchestrator import ExecutionOrchestrator


class ExecutionGate:
    """
    Phase 10 Execution Gate.

    Responsibilities:
    - Bridge lifecycle → execution
    - Enforce lifecycle state before execution
    - Delegate execution without altering intent

    Explicitly NOT responsible for:
    - Scheduling
    - Retries
    - Risk checks
    - Capital sizing
    - Broker logic
    """

    def __init__(
        self,
        *,
        lifecycle_orchestrator: StrategyLifecycleOrchestrator,
        execution_orchestrator: ExecutionOrchestrator,
    ):
        self._lifecycle = lifecycle_orchestrator
        self._execution = execution_orchestrator

    def handle_intent(
        self,
        *,
        strategy_id: str,
        intent: Optional[StrategyIntent],
        order_id: str,
        order_payload: dict,
    ) -> bool:
        """
        Handle a StrategyIntent.

        Returns:
            True  -> execution attempted
            False -> execution blocked or skipped
        """
        # No intent → nothing to do
        if intent is None:
            return False

        # Lifecycle gate
        if not self._lifecycle.can_execute(strategy_id):
            return False

        # Delegate execution
        self._execution.submit_order(
            order_id=order_id,
            order_payload=order_payload,
        )

        return True
