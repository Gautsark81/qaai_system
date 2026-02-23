from typing import List, Dict
from collections import defaultdict
from modules.governance_feedback.approval_outcome import (
    ApprovalOutcome,
    ApprovalOutcomeRecord,
)


class ApprovalBiasDetector:
    def detect(
        self,
        records: List[ApprovalOutcomeRecord],
    ) -> Dict[str, float]:
        """
        Returns approver -> success rate
        """
        grouped = defaultdict(list)

        for r in records:
            grouped[r.approver].append(r.outcome)

        bias = {}
        for approver, outcomes in grouped.items():
            success = outcomes.count(ApprovalOutcome.SUCCESS)
            bias[approver] = round(success / len(outcomes), 4)

        return bias
