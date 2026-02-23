from datetime import datetime

from core.v2.operator_dashboard.actions import OperatorActions
from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState


def test_operator_approve_and_revoke():
    store = ApprovalStore()
    actions = OperatorActions(approval_store=store)
    now = datetime.utcnow()

    rec = actions.approve_live(
        strategy_id="s1",
        operator="op",
        now=now,
        ttl_minutes=10,
        notes="Initial approval",
    )

    assert rec.approved_by == "op"

    revoked = actions.revoke_live(
        strategy_id="s1",
        operator="op",
        now=now,
        reason="manual stop",
    )

    assert "REVOKED" in revoked.notes


def test_operator_pause_strategy():
    lifecycle = StrategyLifecycle(strategy_id="s2")
    lifecycle.state = LifecycleState.PAPER_ACTIVE

    actions = OperatorActions(approval_store=ApprovalStore())
    actions.pause_strategy(lifecycle=lifecycle, reason="investigation")

    assert lifecycle.state == LifecycleState.DECAYING
