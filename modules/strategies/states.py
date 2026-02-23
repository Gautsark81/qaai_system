# modules/strategies/states.py

from enum import Enum


class StrategyState(str, Enum):
    """
    Canonical strategy state enum.

    NOTE:
    - Used by strategy factory, context, health, and tests
    - DO NOT MOVE OR DELETE
    """

    INIT = "INIT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DISABLED = "DISABLED"
    FAILED = "FAILED"
