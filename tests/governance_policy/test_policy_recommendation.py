from modules.governance_policy.policy_recommendation import (
    PolicyRecommendationEngine,
)
from modules.governance_policy.promotion_policy_evaluator import (
    PromotionEvaluationResult,
)


def test_policy_recommendation_engine():
    engine = PolicyRecommendationEngine()

    recs = engine.recommend(
        PromotionEvaluationResult(precision=0.4, recall=0.9)
    )

    assert len(recs) == 1
