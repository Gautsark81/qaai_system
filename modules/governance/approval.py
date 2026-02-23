from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional


class ApprovalDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ApprovalRecord:
    strategy_id: str
    decision: ApprovalDecision
    approver: str
    timestamp: datetime
    expires_at: Optional[datetime]
    reason: str


class ApprovalService:
    def approve(
        self,
        strategy_id: str,
        approver: str,
        reason: str,
        ttl_hours: int = 72,
    ) -> ApprovalRecord:
        now = datetime.utcnow()
        return ApprovalRecord(
            strategy_id=strategy_id,
            decision=ApprovalDecision.APPROVED,
            approver=approver,
            timestamp=now,
            expires_at=now + timedelta(hours=ttl_hours),
            reason=reason,
        )

    def reject(
        self,
        strategy_id: str,
        approver: str,
        reason: str,
    ) -> ApprovalRecord:
        return ApprovalRecord(
            strategy_id=strategy_id,
            decision=ApprovalDecision.REJECTED,
            approver=approver,
            timestamp=datetime.utcnow(),
            expires_at=None,
            reason=reason,
        )
