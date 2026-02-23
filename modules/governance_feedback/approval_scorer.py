from typing import List
from modules.governance_feedback.approval_outcome import (
    ApprovalOutcome,
    ApprovalOutcomeRecord,
)


class ApprovalScorer:
    def score(self, records: List[ApprovalOutcomeRecord]) -> float:
        if not records:
            return 0.0

        successes = sum(
            1 for r in records if r.outcome == ApprovalOutcome.SUCCESS
        )

        return round(successes / len(records), 4)
