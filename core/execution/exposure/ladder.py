from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.capital.arming.contracts import CapitalArmingState


class ExecutionExposureLevel(str, Enum):
    SHADOW = "SHADOW"
    PAPER = "PAPER"
    LIVE = "LIVE"


@dataclass(frozen=True)
class ExecutionExposureLadder:
    """
    Phase 19.0 — Execution Exposure Ladder

    Governs which execution exposure levels are permitted
    under a given capital arming state.

    HARD RULES:
    - Pure and stateless
    - Capital arming is the final authority
    - No side effects
    """

    capital_arming_state: CapitalArmingState

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def is_allowed(self, exposure: ExecutionExposureLevel) -> bool:
        if exposure == ExecutionExposureLevel.SHADOW:
            return True

        if exposure == ExecutionExposureLevel.PAPER:
            return self._paper_allowed()

        if exposure == ExecutionExposureLevel.LIVE:
            return self._live_allowed()

        raise RuntimeError(f"Unknown exposure level: {exposure}")

    # --------------------------------------------------
    # Internal rules (explicit & auditable)
    # --------------------------------------------------

    def _paper_allowed(self) -> bool:
        return self.capital_arming_state in (
            CapitalArmingState.SHADOW,
            CapitalArmingState.PAPER,
            CapitalArmingState.LIVE,
        )

    def _live_allowed(self) -> bool:
        return self.capital_arming_state == CapitalArmingState.LIVE
