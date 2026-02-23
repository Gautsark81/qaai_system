from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SystemArmingState(Enum):
    DISARMED = "disarmed"
    ARMED = "armed"


class ArmingViolation(Exception):
    """Raised when execution is attempted while disarmed."""
    pass


@dataclass(frozen=True)
class ExecutionArming:
    """
    Operator-controlled execution arming state.

    This is a HARD gate:
    - DISARMED → only SHADOW allowed
    - ARMED → governed modes allowed
    """

    state: SystemArmingState

    def assert_execution_allowed(self, *, is_shadow: bool) -> None:
        if self.state == SystemArmingState.DISARMED and not is_shadow:
            raise ArmingViolation(
                "Execution blocked: system is DISARMED"
            )
