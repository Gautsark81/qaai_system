from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from core.capital.arming.contracts import (
    CapitalArmingState,
    CapitalArmingDecision,
)


class CapitalArmingEvaluator:
    """
    Phase 18.0 — Capital Arming Evaluator

    HARD GUARANTEES:
    - No skipping arming levels
    - Deterministic decisions
    - No side effects
    - Governance-first
    """

    _ORDER: List[CapitalArmingState] = [
        CapitalArmingState.DISARMED,
        CapitalArmingState.SHADOW,
        CapitalArmingState.PAPER,
        CapitalArmingState.TINY_LIVE,
        CapitalArmingState.GOVERNED_LIVE,
    ]

    def evaluate(
        self,
        *,
        requested: CapitalArmingState,
        current: CapitalArmingState,
    ) -> CapitalArmingDecision:
        """
        Evaluate whether a requested capital arming transition is allowed.
        """

        # Always block if currently disarmed and requesting non-shadow
        if current == CapitalArmingState.DISARMED:
            if requested != CapitalArmingState.SHADOW:
                return CapitalArmingDecision(
                    state=current,
                    allowed=False,
                    reasons=["System is disarmed"],
                    decided_at=datetime.now(tz=timezone.utc),
                )

        current_idx = self._ORDER.index(current)
        requested_idx = self._ORDER.index(requested)

        # Prevent skipping levels
        if requested_idx > current_idx + 1:
            return CapitalArmingDecision(
                state=current,
                allowed=False,
                reasons=["Cannot skip capital arming levels"],
                decided_at=datetime.now(tz=timezone.utc),
            )

        # Allow linear progression or same-state affirmation
        allowed = requested_idx >= current_idx

        return CapitalArmingDecision(
            state=requested if allowed else current,
            allowed=allowed and requested != CapitalArmingState.DISARMED,
            reasons=[
                "Capital arming allowed"
                if allowed
                else "Capital arming blocked"
            ],
            decided_at=datetime.now(tz=timezone.utc),
        )
