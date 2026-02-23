from __future__ import annotations

from datetime import datetime
from typing import Dict

from core.v2.operator_dashboard.aggregators import DashboardAggregator
from core.v2.operator_dashboard.actions import OperatorActions
from core.v2.paper_capital.lifecycle import StrategyLifecycle
from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveGateDecision


class OperatorCLI:
    """
    Thin CLI adapter for operator actions and dashboards.
    """

    def __init__(
        self,
        *,
        aggregator: DashboardAggregator,
        actions: OperatorActions,
        approval_store: ApprovalStore,
    ):
        self._agg = aggregator
        self._actions = actions
        self._approvals = approval_store

    # ------------------------------------------------------------------
    # READ COMMANDS
    # ------------------------------------------------------------------

    def status(
        self,
        *,
        lifecycle: StrategyLifecycle,
        shadow_pnl: float,
        gate_decision: LiveGateDecision,
        now: datetime,
    ) -> Dict[str, object]:
        return {
            "strategy": self._agg.strategy_status(
                lifecycle=lifecycle,
                shadow_pnl=shadow_pnl,
                now=now,
            ),
            "approval": self._agg.approval_status(
                strategy_id=lifecycle.strategy_id,
                store=self._approvals,
                now=now,
            ),
            "safety": self._agg.safety_status(
                decision=gate_decision,
                now=now,
            ),
        }

    # ------------------------------------------------------------------
    # ACTION COMMANDS
    # ------------------------------------------------------------------

    def approve(
        self,
        *,
        strategy_id: str,
        operator: str,
        ttl_minutes: int,
        notes: str,
        now: datetime,
    ):
        return self._actions.approve_live(
            strategy_id=strategy_id,
            operator=operator,
            now=now,
            ttl_minutes=ttl_minutes,
            notes=notes,
        )

    def revoke(
        self,
        *,
        strategy_id: str,
        operator: str,
        reason: str,
        now: datetime,
    ):
        return self._actions.revoke_live(
            strategy_id=strategy_id,
            operator=operator,
            now=now,
            reason=reason,
        )

    def pause(
        self,
        *,
        lifecycle: StrategyLifecycle,
        reason: str,
    ) -> None:
        self._actions.pause_strategy(
            lifecycle=lifecycle,
            reason=reason,
        )
