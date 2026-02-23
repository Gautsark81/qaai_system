from dataclasses import dataclass
from typing import List
from modules.governance_feedback.kill_attribution import KillAttribution
from modules.governance_feedback.approval_outcome import (
    ApprovalOutcomeRecord,
)
from modules.governance_feedback.approval_scorer import ApprovalScorer


@dataclass(frozen=True)
class GovernanceFeedbackReport:
    kill_events: List[KillAttribution]
    approval_outcomes: List[ApprovalOutcomeRecord]
    approval_score: float


class GovernanceFeedbackBuilder:
    def build(
        self,
        kills: List[KillAttribution],
        outcomes: List[ApprovalOutcomeRecord],
    ) -> GovernanceFeedbackReport:

        score = ApprovalScorer().score(outcomes)

        return GovernanceFeedbackReport(
            kill_events=kills,
            approval_outcomes=outcomes,
            approval_score=score,
        )
