# test_phase11_deterministic_decision.py

from core.strategy_factory.promotion.eligibility import PromotionEligibilityEvaluator

def test_promotion_decision_is_deterministic():
    evaluator = PromotionEligibilityEvaluator(ssr_threshold=0.8)

    d1 = evaluator.evaluate("STRAT_X", ssr=0.85)
    d2 = evaluator.evaluate("STRAT_X", ssr=0.85)

    assert d1 == d2
