# File: core/strategy_factory/promotion/wiring/shadow_to_paper_wiring.py

from core.strategy_factory.promotion.eligibility import PromotionDecision
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)
from core.strategy_factory.promotion.wiring.wiring_recommendation import (
    WiringRecommendation,
)


class ShadowToPaperWiringEvaluator:
    """
    Phase 11.3 — Evaluates whether a SHADOW strategy
    should be recommended for PAPER wiring.

    This class is descriptive only.
    """

    def evaluate(
        self,
        *,
        strategy_id: str,
        current_state: PromotionState,
        promotion_decision: PromotionDecision,
    ) -> WiringRecommendation | None:
        if current_state is not PromotionState.SHADOW:
            return None

        if not promotion_decision.eligible:
            return None

        return WiringRecommendation(
            strategy_id=strategy_id,
            from_state=PromotionState.SHADOW,
            to_state=PromotionState.PAPER,
            reason="Promotion eligibility satisfied",
        )
