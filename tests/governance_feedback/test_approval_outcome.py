from modules.governance_feedback.approval_outcome import (
    ApprovalOutcome,
    ApprovalOutcomeRecord,
)


def test_approval_outcome_record():
    rec = ApprovalOutcomeRecord(
        "s1", "admin", ApprovalOutcome.SUCCESS, 48.0
    )

    assert rec.outcome == ApprovalOutcome.SUCCESS
