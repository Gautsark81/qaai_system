from __future__ import annotations

from datetime import datetime

from core.v2.operator_dashboard.cli import OperatorCLI
from core.v2.operator_dashboard.aggregators import DashboardAggregator
from core.v2.operator_dashboard.actions import OperatorActions
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState
from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveGateDecision


def run_drill_manual_revoke(
    *,
    strategy_id: str,
    operator: str,
) -> None:
    """
    Drill 2: Manual Revoke
    """

    now = datetime.utcnow()

    approval_store = ApprovalStore()
    actions = OperatorActions(approval_store=approval_store)
    aggregator = DashboardAggregator()
    cli = OperatorCLI(
        aggregator=aggregator,
        actions=actions,
        approval_store=approval_store,
    )

    lifecycle = StrategyLifecycle(strategy_id=strategy_id)
    lifecycle.state = LifecycleState.PAPER_ACTIVE

    gate = LiveGateDecision(
        strategy_id=strategy_id,
        allowed=False,
        reasons=["no_active_approval"],
        evaluated_at=now,
    )

    # --- Step 2.1: Issue long approval ---
    cli.approve(
        strategy_id=strategy_id,
        operator=operator,
        ttl_minutes=60,
        notes="Drill 2 — manual revoke test",
        now=now,
    )

    status_before = cli.status(
        lifecycle=lifecycle,
        shadow_pnl=0.0,
        gate_decision=gate,
        now=now,
    )

    assert status_before["approval"].approved is True

    # --- Step 2.2: Manual revoke ---
    cli.revoke(
        strategy_id=strategy_id,
        operator=operator,
        reason="Drill 2 emergency stop",
        now=datetime.utcnow(),
    )

    status_after = cli.status(
        lifecycle=lifecycle,
        shadow_pnl=0.0,
        gate_decision=gate,
        now=datetime.utcnow(),
    )

    assert status_after["approval"].approved is False
    assert status_after["safety"].live_allowed is False
