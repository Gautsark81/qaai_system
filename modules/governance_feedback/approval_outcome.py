from dataclasses import dataclass
from enum import Enum


class ApprovalOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED_EARLY = "FAILED_EARLY"
    FAILED_LATE = "FAILED_LATE"


@dataclass(frozen=True)
class ApprovalOutcomeRecord:
    strategy_id: str
    approver: str
    outcome: ApprovalOutcome
    live_duration_hours: float
