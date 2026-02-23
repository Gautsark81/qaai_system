from __future__ import annotations

from datetime import datetime

from core.v2.operator_dashboard.cli import OperatorCLI
from core.v2.operator_dashboard.aggregators import DashboardAggregator
from core.v2.operator_dashboard.actions import OperatorActions
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState
from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveGateDecision


def run_drill_operator_uncertainty(
    *,
    strategy_id: str,
    operator: str,
) -> None:
    """
    Drill 5: Operator uncertainty → HALT FIRST
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

    # --- Create ambiguous situation ---
    cli.approve(
        strategy_id=strategy_id,
        operator=operator,
        ttl_minutes=60,
        notes="Drill 5 — ambiguous state",
        now=now,
    )

    ambiguous_gate = LiveGateDecision(
        strategy_id=strategy_id,
        allowed=False,
        reasons=["unexpected_condition"],
        evaluated_at=now,
    )

    # --- Operator chooses HALT ---
    cli.revoke(
        strategy_id=strategy_id,
        operator=operator,
        reason="Drill 5 — operator uncertainty",
        now=now,
    )

    cli.pause(
        lifecycle=lifecycle,
        reason="Drill 5 — halt first",
    )

    # --- Verify safe terminal state ---
    status = cli.status(
        lifecycle=lifecycle,
        shadow_pnl=0.0,
        gate_decision=ambiguous_gate,
        now=now,
    )

    assert status["approval"].approved is False
    assert status["strategy"].lifecycle_state == "decaying"
    assert status["safety"].live_allowed is False
