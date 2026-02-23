from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SystemArmingState(Enum):
    """
    Global execution arming state.

    DISARMED:
        - Only shadow execution allowed
        - Paper / Live execution blocked

    ARMED:
        - Governed execution permitted
    """

    DISARMED = "disarmed"
    ARMED = "armed"


class ArmingViolation(Exception):
    """
    Raised when execution is attempted while system is disarmed.
    """
    pass


@dataclass(frozen=True)
class ExecutionArming:
    """
    Immutable execution arming authority.

    Laws:
    - Read-only
    - Deterministic
    - No side effects
    - Operator-controlled
    """

    state: SystemArmingState

    @property
    def is_armed(self) -> bool:
        return self.state == SystemArmingState.ARMED

    def assert_execution_allowed(self) -> None:
        if not self.is_armed:
            raise ArmingViolation(
                "Execution blocked: system is DISARMED"
            )
