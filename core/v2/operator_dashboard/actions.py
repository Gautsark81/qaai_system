from __future__ import annotations

from datetime import datetime, timedelta

from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveApprovalRecord
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState


class OperatorActions:
    """
    Human-gated operator actions.
    """

    def __init__(self, *, approval_store: ApprovalStore):
        self._store = approval_store

    def approve_live(
        self,
        *,
        strategy_id: str,
        operator: str,
        now: datetime,
        ttl_minutes: int,
        notes: str,
    ) -> LiveApprovalRecord:
        record = LiveApprovalRecord(
            strategy_id=strategy_id,
            approved_by=operator,
            approved_at=now,
            expires_at=now + timedelta(minutes=ttl_minutes),
            notes=notes,
        )
        self._store.add(record)
        return record

    def revoke_live(
        self,
        *,
        strategy_id: str,
        operator: str,
        now: datetime,
        reason: str,
    ) -> LiveApprovalRecord:
        # Immediate expiry record (append-only)
        record = LiveApprovalRecord(
            strategy_id=strategy_id,
            approved_by=operator,
            approved_at=now,
            expires_at=now,  # expired immediately
            notes=f"REVOKED: {reason}",
        )
        self._store.add(record)
        return record

    def pause_strategy(
        self,
        *,
        lifecycle: StrategyLifecycle,
        reason: str,
    ) -> None:
        # Hard safety pause
        lifecycle.state = LifecycleState.DECAYING
