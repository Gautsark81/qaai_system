from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.execution.execution_mode import ExecutionMode


class GovernanceViolation(Exception):
    """Raised when an execution mode is not permitted."""
    pass


class ExecutionPromotion(Enum):
    SHADOW_ONLY = "shadow_only"
    SHADOW_AND_PAPER = "shadow_and_paper"
    ALL_MODES = "all_modes"  # LIVE allowed in future


@dataclass(frozen=True)
class ExecutionGovernance:
    """
    Central authority for execution mode governance.

    This is the ONLY place where execution mode permissions
    are defined and enforced.
    """

    promotion_level: ExecutionPromotion

    def is_allowed(self, mode: ExecutionMode) -> bool:
        if self.promotion_level == ExecutionPromotion.SHADOW_ONLY:
            return mode == ExecutionMode.SHADOW

        if self.promotion_level == ExecutionPromotion.SHADOW_AND_PAPER:
            return mode in (ExecutionMode.SHADOW, ExecutionMode.PAPER)

        if self.promotion_level == ExecutionPromotion.ALL_MODES:
            return True

        return False

    def assert_allowed(self, mode: ExecutionMode) -> None:
        if not self.is_allowed(mode):
            raise GovernanceViolation(
                f"Execution mode '{mode.value}' is not allowed "
                f"under promotion level '{self.promotion_level.value}'"
            )
