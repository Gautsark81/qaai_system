# test_phase11_ssr_threshold.py

from core.strategy_factory.promotion.eligibility import PromotionEligibilityEvaluator

def test_strategy_below_ssr_threshold_is_not_eligible():
    evaluator = PromotionEligibilityEvaluator(ssr_threshold=0.8)

    decision = evaluator.evaluate(
        strategy_id="STRAT_LOW",
        ssr=0.72,
    )

    assert decision.eligible is False
