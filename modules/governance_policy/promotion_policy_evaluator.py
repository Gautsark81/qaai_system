from dataclasses import dataclass
from typing import List
from modules.governance_feedback.approval_outcome import ApprovalOutcome


@dataclass(frozen=True)
class PromotionEvaluationResult:
    precision: float
    recall: float


class PromotionPolicyEvaluator:
    def evaluate(
        self,
        promoted_outcomes: List[ApprovalOutcome],
        rejected_outcomes: List[ApprovalOutcome],
    ) -> PromotionEvaluationResult:
        tp = promoted_outcomes.count(ApprovalOutcome.SUCCESS)
        fp = len(promoted_outcomes) - tp

        fn = rejected_outcomes.count(ApprovalOutcome.SUCCESS)

        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0

        return PromotionEvaluationResult(
            precision=round(precision, 4),
            recall=round(recall, 4),
        )
