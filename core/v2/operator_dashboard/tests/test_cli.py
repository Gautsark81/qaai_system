from datetime import datetime, timedelta

from core.v2.operator_dashboard.cli import OperatorCLI
from core.v2.operator_dashboard.aggregators import DashboardAggregator
from core.v2.operator_dashboard.actions import OperatorActions
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState
from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveGateDecision


def test_cli_status_and_actions():
    store = ApprovalStore()
    agg = DashboardAggregator()
    actions = OperatorActions(approval_store=store)
    cli = OperatorCLI(
        aggregator=agg,
        actions=actions,
        approval_store=store,
    )

    now = datetime.utcnow()

    lifecycle = StrategyLifecycle(strategy_id="s1")
    lifecycle.state = LifecycleState.PAPER_ACTIVE

    gate = LiveGateDecision(
        strategy_id="s1",
        allowed=False,
        reasons=["no_active_approval"],
        evaluated_at=now,
    )

    status = cli.status(
        lifecycle=lifecycle,
        shadow_pnl=10.0,
        gate_decision=gate,
        now=now,
    )

    assert status["strategy"].lifecycle_state == "paper_active"
    assert status["approval"].approved is False
    assert status["safety"].live_allowed is False

    cli.approve(
        strategy_id="s1",
        operator="op",
        ttl_minutes=5,
        notes="test",
        now=now,
    )

    status2 = cli.status(
        lifecycle=lifecycle,
        shadow_pnl=10.0,
        gate_decision=gate,
        now=now + timedelta(seconds=1),
    )

    assert status2["approval"].approved is True

    cli.pause(
        lifecycle=lifecycle,
        reason="manual pause",
    )

    assert lifecycle.state == LifecycleState.DECAYING
