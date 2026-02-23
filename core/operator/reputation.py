# core/operator/reputation.py
from dataclasses import dataclass
from typing import List
from core.operator.operator_event import OperatorEvent, OperatorEventType


@dataclass(frozen=True)
class OperatorReputation:
    operator_id: str
    total_events: int
    override_count: int
    approval_count: int
    intervention_count: int

    @property
    def override_ratio(self) -> float:
        if self.total_events == 0:
            return 0.0
        return self.override_count / self.total_events


def compute_reputation(
    operator_id: str,
    events: List[OperatorEvent],
) -> OperatorReputation:
    relevant = [e for e in events if e.operator_id == operator_id]

    override_count = sum(1 for e in relevant if e.event_type == OperatorEventType.OVERRIDE)
    approval_count = sum(1 for e in relevant if e.event_type == OperatorEventType.APPROVAL)
    intervention_count = sum(
        1 for e in relevant if e.event_type == OperatorEventType.INTERVENTION
    )

    return OperatorReputation(
        operator_id=operator_id,
        total_events=len(relevant),
        override_count=override_count,
        approval_count=approval_count,
        intervention_count=intervention_count,
    )
