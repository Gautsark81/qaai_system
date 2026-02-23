# modules/strategy_lifecycle/states.py

from enum import Enum


class StrategyState(str, Enum):
    """
    Phase 9 lifecycle state.

    NOTE:
    - Name is REQUIRED by tests
    - This is NOT the same enum as modules.strategies.states.StrategyState
    - Identical values, different domain
    """

    INIT = "INIT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DISABLED = "DISABLED"
    FAILED = "FAILED"
