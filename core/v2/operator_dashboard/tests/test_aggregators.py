from datetime import datetime, timedelta

from core.v2.operator_dashboard.aggregators import DashboardAggregator
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState
from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveApprovalRecord, LiveGateDecision


def test_strategy_status_aggregation():
    agg = DashboardAggregator()
    lifecycle = StrategyLifecycle(strategy_id="s1")
    lifecycle.state = LifecycleState.PAPER_ACTIVE

    status = agg.strategy_status(
        lifecycle=lifecycle,
        shadow_pnl=12.5,
        now=datetime.utcnow(),
    )

    assert status.lifecycle_state == "paper_active"
    assert status.shadow_pnl == 12.5


def test_approval_status_aggregation():
    agg = DashboardAggregator()
    store = ApprovalStore()
    now = datetime.utcnow()

    store.add(
        LiveApprovalRecord(
            strategy_id="s1",
            approved_by="op",
            approved_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(minutes=5),
            notes="OK",
        )
    )

    status = agg.approval_status(
        strategy_id="s1",
        store=store,
        now=now,
    )

    assert status.approved is True
    assert status.approved_by == "op"


def test_safety_status_aggregation():
    agg = DashboardAggregator()
    decision = LiveGateDecision(
        strategy_id="s1",
        allowed=False,
        reasons=["no_active_approval"],
        evaluated_at=datetime.utcnow(),
    )

    status = agg.safety_status(
        decision=decision,
        now=datetime.utcnow(),
    )

    assert status.live_allowed is False
    assert "approval" in status.reason_summary
