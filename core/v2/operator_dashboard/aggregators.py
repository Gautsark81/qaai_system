from __future__ import annotations

from datetime import datetime
from typing import List

from core.v2.operator_dashboard.contracts import (
    StrategyStatus,
    ApprovalStatus,
    SafetyStatus,
)
from core.v2.paper_capital.lifecycle import StrategyLifecycle
from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveGateDecision


class DashboardAggregator:
    """
    Read-only aggregator for operator dashboards.
    """

    def strategy_status(
        self,
        *,
        lifecycle: StrategyLifecycle,
        shadow_pnl: float,
        now: datetime,
    ) -> StrategyStatus:
        return StrategyStatus(
            strategy_id=lifecycle.strategy_id,
            lifecycle_state=lifecycle.state.value,
            shadow_pnl=shadow_pnl,
            last_updated=now,
        )

    def approval_status(
        self,
        *,
        strategy_id: str,
        store: ApprovalStore,
        now: datetime,
    ) -> ApprovalStatus:
        active = store.get_active(strategy_id=strategy_id, now=now)

        if active is None:
            return ApprovalStatus(
                strategy_id=strategy_id,
                approved=False,
                approved_by=None,
                expires_at=None,
            )

        return ApprovalStatus(
            strategy_id=strategy_id,
            approved=True,
            approved_by=active.approved_by,
            expires_at=active.expires_at,
        )

    def safety_status(
        self,
        *,
        decision: LiveGateDecision,
        now: datetime,
    ) -> SafetyStatus:
        reason = ",".join(decision.reasons) if decision.reasons else "ok"

        return SafetyStatus(
            strategy_id=decision.strategy_id,
            live_allowed=decision.allowed,
            last_check=now,
            reason_summary=reason,
        )
