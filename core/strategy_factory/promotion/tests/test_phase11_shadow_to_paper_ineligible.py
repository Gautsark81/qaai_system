from core.strategy_factory.promotion.wiring.shadow_to_paper_wiring import (
    ShadowToPaperWiringEvaluator,
)
from core.strategy_factory.promotion.eligibility import (
    PromotionEligibilityEvaluator,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_ineligible_strategy_gets_no_wiring_recommendation():
    eligibility = PromotionEligibilityEvaluator(ssr_threshold=0.8)
    decision = eligibility.evaluate("STRAT_BAD", ssr=0.6)

    evaluator = ShadowToPaperWiringEvaluator()

    rec = evaluator.evaluate(
        strategy_id="STRAT_BAD",
        current_state=PromotionState.SHADOW,
        promotion_decision=decision,
    )

    assert rec is None
