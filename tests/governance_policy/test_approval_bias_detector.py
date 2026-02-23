from modules.governance_policy.approval_bias_detector import (
    ApprovalBiasDetector,
)
from modules.governance_feedback.approval_outcome import (
    ApprovalOutcome,
    ApprovalOutcomeRecord,
)


def test_approval_bias_detector():
    records = [
        ApprovalOutcomeRecord("s1", "A", ApprovalOutcome.SUCCESS, 48),
        ApprovalOutcomeRecord("s2", "A", ApprovalOutcome.FAILED_EARLY, 2),
        ApprovalOutcomeRecord("s3", "B", ApprovalOutcome.SUCCESS, 36),
    ]

    bias = ApprovalBiasDetector().detect(records)

    assert bias["A"] == 0.5
    assert bias["B"] == 1.0
