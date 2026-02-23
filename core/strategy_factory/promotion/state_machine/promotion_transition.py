# File: core/strategy_factory/promotion/state_machine/promotion_transition.py

from dataclasses import dataclass
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


@dataclass(frozen=True)
class PromotionTransition:
    """
    Phase 11.2 — Descriptive transition only.
    No execution, no capital, no side effects.
    """

    from_state: PromotionState
    to_state: PromotionState
    reason: str
