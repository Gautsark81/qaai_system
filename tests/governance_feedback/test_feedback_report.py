from modules.governance_feedback.feedback_report import (
    GovernanceFeedbackBuilder,
)
from modules.governance_feedback.kill_attribution import (
    KillAttribution,
    KillReason,
)
from modules.governance_feedback.approval_outcome import (
    ApprovalOutcome,
    ApprovalOutcomeRecord,
)


def test_feedback_report_build():
    kills = [
        KillAttribution("s1", KillReason.DRAWDOWN, "Exceeded DD"),
    ]

    outcomes = [
        ApprovalOutcomeRecord(
            "s1", "admin", ApprovalOutcome.FAILED_EARLY, 1.5
        )
    ]

    report = GovernanceFeedbackBuilder().build(kills, outcomes)

    assert report.approval_score == 0.0
