from modules.governance_policy.promotion_policy_evaluator import (
    PromotionPolicyEvaluator,
)
from modules.governance_feedback.approval_outcome import ApprovalOutcome


def test_promotion_policy_evaluator():
    evaluator = PromotionPolicyEvaluator()

    result = evaluator.evaluate(
        promoted_outcomes=[
            ApprovalOutcome.SUCCESS,
            ApprovalOutcome.FAILED_EARLY,
        ],
        rejected_outcomes=[ApprovalOutcome.SUCCESS],
    )

    assert result.precision == 0.5
    assert result.recall == 0.5
