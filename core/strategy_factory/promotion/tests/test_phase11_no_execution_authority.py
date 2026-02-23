# test_phase11_no_execution_authority.py

from core.strategy_factory.promotion.eligibility import PromotionEligibilityEvaluator

def test_promotion_logic_has_no_execution_side_effects():
    evaluator = PromotionEligibilityEvaluator(ssr_threshold=0.8)

    decision = evaluator.evaluate(
        strategy_id="STRAT_SAFE",
        ssr=0.85,
    )

    assert not hasattr(evaluator, "execute")
    assert not hasattr(decision, "execute")
