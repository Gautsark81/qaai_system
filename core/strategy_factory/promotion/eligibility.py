# File: core/strategy_factory/promotion/eligibility.py

from core.strategy_factory.promotion.promotion_decision import PromotionDecision
from core.strategy_factory.promotion.promotion_reason import PromotionReason


class PromotionEligibilityEvaluator:
    """
    Phase 11.1 — Determines promotion eligibility using SSR only.
    Deterministic, stateless, side-effect free.
    """

    def __init__(self, *, ssr_threshold: float):
        self._ssr_threshold = float(ssr_threshold)

    def evaluate(self, strategy_id: str, *, ssr: float) -> PromotionDecision:
        if ssr >= self._ssr_threshold:
            return PromotionDecision(
                strategy_id=strategy_id,
                eligible=True,
                reasons=[PromotionReason.SSR_ABOVE_THRESHOLD.value],
            )

        return PromotionDecision(
            strategy_id=strategy_id,
            eligible=False,
            reasons=[PromotionReason.SSR_BELOW_THRESHOLD.value],
        )
