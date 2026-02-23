from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List

# ✅ FIX: import from EXISTING canonical module
from core.strategy_factory.promotion.engine import PromotionDecision


# ------------------------------------------------------------------
# Lifecycle States
# ------------------------------------------------------------------

class PromotionLifecycleState(str, Enum):
    CANDIDATE = "CANDIDATE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ------------------------------------------------------------------
# Transition Record (Immutable)
# ------------------------------------------------------------------

@dataclass(frozen=True)
class PromotionLifecycleTransition:
    from_state: PromotionLifecycleState
    to_state: PromotionLifecycleState
    timestamp: datetime


# ------------------------------------------------------------------
# Lifecycle State Machine
# ------------------------------------------------------------------

class PromotionLifecycleMachine:
    """
    Phase 17.2 — Promotion Lifecycle State Machine

    HARD GUARANTEES:
    - Deterministic state transitions
    - Explicit terminal states
    - Immutable transition history
    - No re-promotion
    - No resurrection from rejection
    """

    def __init__(self, *, strategy_dna: str):
        self.strategy_dna = strategy_dna
        self._state: PromotionLifecycleState = PromotionLifecycleState.CANDIDATE
        self._history: List[PromotionLifecycleTransition] = []

    # ------------------------------------------------------------------
    # Public State
    # ------------------------------------------------------------------

    @property
    def state(self) -> PromotionLifecycleState:
        return self._state

    # ------------------------------------------------------------------
    # Apply Promotion Decision
    # ------------------------------------------------------------------

    def apply_decision(self, decision: PromotionDecision) -> None:
        """
        Apply a PromotionDecision to the lifecycle machine.

        Rules:
        - CANDIDATE → APPROVED (if promoted)
        - CANDIDATE → REJECTED (if blocked)
        - APPROVED / REJECTED are terminal
        """

        if self._state in (
            PromotionLifecycleState.APPROVED,
            PromotionLifecycleState.REJECTED,
        ):
            raise RuntimeError(
                f"Cannot apply decision in terminal state: {self._state}"
            )

        if self._state != PromotionLifecycleState.CANDIDATE:
            raise RuntimeError(
                f"Illegal lifecycle state: {self._state}"
            )

        next_state = (
            PromotionLifecycleState.APPROVED
            if decision.promoted
            else PromotionLifecycleState.REJECTED
        )

        transition = PromotionLifecycleTransition(
            from_state=self._state,
            to_state=next_state,
            timestamp=datetime.now(tz=timezone.utc),
        )

        self._history.append(transition)
        self._state = next_state

    # ------------------------------------------------------------------
    # Audit History (Read-only)
    # ------------------------------------------------------------------

    def history(self) -> List[PromotionLifecycleTransition]:
        """
        Return an immutable copy of transition history.
        """
        return list(self._history)
