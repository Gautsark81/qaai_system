from datetime import datetime, timedelta

from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveApprovalRecord
from core.v2.live_bridge.guards.live_gate import LiveGate
from core.v2.paper_capital.lifecycle import StrategyLifecycle, LifecycleState


def test_live_gate_allows_with_active_approval_and_active_lifecycle():
    store = ApprovalStore()
    now = datetime.utcnow()

    store.add(
        LiveApprovalRecord(
            strategy_id="s1",
            approved_by="operator",
            approved_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(minutes=5),
            notes="OK",
        )
    )

    lifecycle = StrategyLifecycle(strategy_id="s1")
    lifecycle.state = LifecycleState.PAPER_ACTIVE

    gate = LiveGate(approval_store=store)

    decision = gate.evaluate(
        strategy_id="s1",
        lifecycle=lifecycle,
        now=now,
    )

    assert decision.allowed is True
    assert decision.reasons == []


def test_live_gate_denies_without_approval():
    store = ApprovalStore()
    now = datetime.utcnow()

    lifecycle = StrategyLifecycle(strategy_id="s2")
    lifecycle.state = LifecycleState.PAPER_ACTIVE

    gate = LiveGate(approval_store=store)

    decision = gate.evaluate(
        strategy_id="s2",
        lifecycle=lifecycle,
        now=now,
    )

    assert decision.allowed is False
    assert "no_active_approval" in decision.reasons


def test_live_gate_denies_on_bad_lifecycle():
    store = ApprovalStore()
    now = datetime.utcnow()

    store.add(
        LiveApprovalRecord(
            strategy_id="s3",
            approved_by="operator",
            approved_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(minutes=5),
            notes="OK",
        )
    )

    lifecycle = StrategyLifecycle(strategy_id="s3")
    lifecycle.state = LifecycleState.DECAYING

    gate = LiveGate(approval_store=store)

    decision = gate.evaluate(
        strategy_id="s3",
        lifecycle=lifecycle,
        now=now,
    )

    assert decision.allowed is False
    assert "lifecycle=decaying" in decision.reasons
