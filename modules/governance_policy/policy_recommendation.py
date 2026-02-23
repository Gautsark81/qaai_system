from dataclasses import dataclass
from typing import List
from modules.governance_policy.promotion_policy_evaluator import (
    PromotionEvaluationResult,
)


@dataclass(frozen=True)
class PolicyRecommendation:
    message: str


class PolicyRecommendationEngine:
    def recommend(
        self,
        promotion_eval: PromotionEvaluationResult,
    ) -> List[PolicyRecommendation]:

        recs = []

        if promotion_eval.precision < 0.6:
            recs.append(
                PolicyRecommendation(
                    "Promotion precision is low. Consider raising SSR threshold."
                )
            )

        if promotion_eval.recall < 0.6:
            recs.append(
                PolicyRecommendation(
                    "Promotion recall is low. Consider relaxing filters."
                )
            )

        return recs
