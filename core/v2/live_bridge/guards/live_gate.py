from __future__ import annotations

from datetime import datetime
from typing import List

from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveGateDecision
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState


class LiveGate:
    """
    Final gate before live trading is allowed.
    """

    def __init__(self, *, approval_store: ApprovalStore):
        self._approvals = approval_store

    def evaluate(
        self,
        *,
        strategy_id: str,
        lifecycle: StrategyLifecycle,
        now: datetime,
    ) -> LiveGateDecision:
        reasons: List[str] = []

        approval = self._approvals.get_active(
            strategy_id=strategy_id,
            now=now,
        )

        if approval is None:
            reasons.append("no_active_approval")

        if lifecycle.state != LifecycleState.PAPER_ACTIVE:
            reasons.append(f"lifecycle={lifecycle.state.value}")

        allowed = len(reasons) == 0

        return LiveGateDecision(
            strategy_id=strategy_id,
            allowed=allowed,
            reasons=reasons,
            evaluated_at=now,
        )
