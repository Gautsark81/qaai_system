from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List


class LiveGovernanceStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class LiveGovernanceDecision:
    """
    Immutable human approval decision for LIVE deployment.
    """

    run_id: str
    strategy_id: str
    status: LiveGovernanceStatus
    reviewer: str
    reasons: List[str]
    decided_at: datetime

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
