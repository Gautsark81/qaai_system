from modules.governance_feedback.approval_scorer import ApprovalScorer
from modules.governance_feedback.approval_outcome import (
    ApprovalOutcome,
    ApprovalOutcomeRecord,
)


def test_approval_scorer():
    records = [
        ApprovalOutcomeRecord("s1", "admin", ApprovalOutcome.SUCCESS, 48),
        ApprovalOutcomeRecord("s2", "admin", ApprovalOutcome.FAILED_EARLY, 2),
    ]

    score = ApprovalScorer().score(records)
    assert score == 0.5
