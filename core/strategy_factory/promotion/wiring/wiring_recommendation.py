# File: core/strategy_factory/promotion/wiring/wiring_recommendation.py

from dataclasses import dataclass
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


@dataclass(frozen=True)
class WiringRecommendation:
    """
    Phase 11.3 — Descriptive wiring recommendation only.
    No execution, no capital, no side effects.
    """

    strategy_id: str
    from_state: PromotionState
    to_state: PromotionState
    reason: str
