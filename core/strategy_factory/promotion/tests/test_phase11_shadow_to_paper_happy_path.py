from core.strategy_factory.promotion.wiring.shadow_to_paper_wiring import (
    ShadowToPaperWiringEvaluator,
)
from core.strategy_factory.promotion.eligibility import (
    PromotionEligibilityEvaluator,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_eligible_shadow_strategy_gets_paper_recommendation():
    eligibility = PromotionEligibilityEvaluator(ssr_threshold=0.8)
    decision = eligibility.evaluate("STRAT_OK", ssr=0.85)

    evaluator = ShadowToPaperWiringEvaluator()

    rec = evaluator.evaluate(
        strategy_id="STRAT_OK",
        current_state=PromotionState.SHADOW,
        promotion_decision=decision,
    )

    assert rec is not None
    assert rec.from_state == PromotionState.SHADOW
    assert rec.to_state == PromotionState.PAPER
