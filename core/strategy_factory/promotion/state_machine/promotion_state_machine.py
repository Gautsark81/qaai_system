# File: core/strategy_factory/promotion/state_machine/promotion_state_machine.py

from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


class PromotionStateMachine:
    """
    Phase 11.2 — Promotion State Machine

    Validates allowed promotion transitions.
    Descriptive only. No execution, capital, or arming authority.
    """

    _ALLOWED_TRANSITIONS = {
        PromotionState.SHADOW: {PromotionState.PAPER},
        PromotionState.PAPER: {PromotionState.TINY_LIVE},
        PromotionState.TINY_LIVE: {PromotionState.LIVE},
        PromotionState.LIVE: set(),
    }

    def can_transition(
        self,
        from_state: PromotionState,
        to_state: PromotionState,
    ) -> bool:
        if from_state == to_state:
            return False

        return to_state in self._ALLOWED_TRANSITIONS.get(from_state, set())
