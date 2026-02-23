from core.strategy_factory.promotion.wiring.shadow_to_paper_wiring import (
    ShadowToPaperWiringEvaluator,
)
from core.strategy_factory.promotion.eligibility import (
    PromotionEligibilityEvaluator,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_non_shadow_state_produces_no_recommendation():
    eligibility = PromotionEligibilityEvaluator(ssr_threshold=0.8)
    decision = eligibility.evaluate("STRAT_OK", ssr=0.9)

    evaluator = ShadowToPaperWiringEvaluator()

    rec = evaluator.evaluate(
        strategy_id="STRAT_OK",
        current_state=PromotionState.PAPER,
        promotion_decision=decision,
    )

    assert rec is None
