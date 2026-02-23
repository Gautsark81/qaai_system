from __future__ import annotations

import time
from datetime import datetime, timedelta

from core.v2.operator_dashboard.cli import OperatorCLI
from core.v2.operator_dashboard.aggregators import DashboardAggregator
from core.v2.operator_dashboard.actions import OperatorActions
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState
from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveGateDecision


def run_drill_approval_expiry(
    *,
    strategy_id: str,
    operator: str,
    ttl_seconds: int = 120,
) -> None:
    """
    Drill 1: Approval Expiry
    """

    now = datetime.utcnow()

    # --- System wiring (real components) ---
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

    # --- Step 1.1: Baseline check ---
    baseline = cli.status(
        lifecycle=lifecycle,
        shadow_pnl=0.0,
        gate_decision=gate,
        now=now,
    )

    assert baseline["approval"].approved is False
    assert baseline["safety"].live_allowed is False

    # --- Step 1.2: Issue approval ---
    cli.approve(
        strategy_id=strategy_id,
        operator=operator,
        ttl_minutes=ttl_seconds // 60,
        notes="Drill 1 — approval expiry test",
        now=now,
    )

    immediate = cli.status(
        lifecycle=lifecycle,
        shadow_pnl=0.0,
        gate_decision=gate,
        now=now,
    )

    assert immediate["approval"].approved is True

    # --- Step 1.4: Passive wait ---
    time.sleep(ttl_seconds + 5)

    # --- Step 1.5: Post-expiry verification ---
    after = cli.status(
        lifecycle=lifecycle,
        shadow_pnl=0.0,
        gate_decision=gate,
        now=datetime.utcnow(),
    )

    assert after["approval"].approved is False
    assert after["safety"].live_allowed is False
