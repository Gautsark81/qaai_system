from typing import Dict
from modules.strategy_lifecycle.states import StrategyState


class StrategyLifecycleStore:
    """
    Deterministic lifecycle state store.

    Phase 9:
    - In-memory
    - Restart-safe
    - No side effects
    """

    def __init__(self):
        self._state: Dict[str, StrategyState] = {}

    def get_state(self, strategy_id: str) -> StrategyState:
        return self._state.get(strategy_id, StrategyState.INIT)

    def set_state(self, strategy_id: str, state: StrategyState) -> None:
        self._state[strategy_id] = state

    def is_active(self, strategy_id: str) -> bool:
        return self.get_state(strategy_id) == StrategyState.ACTIVE
