from modules.intelligence.promotion import PromotionEvaluator
from modules.intelligence.health import StrategyHealth


def test_promotion_pass():
    decision = PromotionEvaluator().evaluate(0.85, StrategyHealth.HEALTHY)
    assert decision.eligible is True


def test_promotion_fail():
    decision = PromotionEvaluator().evaluate(0.6, StrategyHealth.HEALTHY)
    assert decision.eligible is False
