# core/tournament/governance_contracts.py

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List


class GovernanceStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class GovernanceDecision:
    """
    Immutable governance decision for a promoted strategy.
    """

    run_id: str
    strategy_id: str
    status: GovernanceStatus
    reviewer: str
    reasons: List[str]
    decided_at: datetime

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
