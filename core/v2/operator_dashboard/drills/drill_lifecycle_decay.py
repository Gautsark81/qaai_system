from __future__ import annotations

from datetime import datetime

from core.v2.operator_dashboard.cli import OperatorCLI
from core.v2.operator_dashboard.aggregators import DashboardAggregator
from core.v2.operator_dashboard.actions import OperatorActions
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState
from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveGateDecision
from core.v2.live_bridge.guards.live_gate import LiveGate


def run_drill_lifecycle_decay(
    *,
    strategy_id: str,
    operator: str,
) -> None:
    """
    Drill 3: Lifecycle Decay overrides approval
    """

    now = datetime.utcnow()

    # --- System wiring ---
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

    gate_engine = LiveGate(approval_store=approval_store)

    # --- Step 3.1: Issue approval ---
    cli.approve(
        strategy_id=strategy_id,
        operator=operator,
        ttl_minutes=60,
        notes="Drill 3 — lifecycle decay test",
        now=now,
    )

    decision_before = gate_engine.evaluate(
        strategy_id=strategy_id,
        lifecycle=lifecycle,
        now=now,
    )

    assert decision_before.allowed is True

    # --- Step 3.2: Force lifecycle decay ---
    cli.pause(
        lifecycle=lifecycle,
        reason="Drill 3 forced decay",
    )

    assert lifecycle.state == LifecycleState.DECAYING

    # --- Step 3.3: Re-evaluate gate ---
    decision_after = gate_engine.evaluate(
        strategy_id=strategy_id,
        lifecycle=lifecycle,
        now=datetime.utcnow(),
    )

    assert decision_after.allowed is False
    assert "lifecycle=decaying" in decision_after.reasons
