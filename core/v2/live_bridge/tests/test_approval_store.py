from datetime import datetime, timedelta

import pytest

from core.v2.live_bridge.approvals.approval_store import ApprovalStore
from core.v2.live_bridge.contracts import LiveApprovalRecord


def test_add_and_get_active():
    store = ApprovalStore()
    now = datetime.utcnow()

    record = LiveApprovalRecord(
        strategy_id="s1",
        approved_by="operator",
        approved_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=1),
        notes="OK",
    )

    store.add(record)

    active = store.get_active(strategy_id="s1", now=now)
    assert active == record


def test_expired_approval_returns_none():
    store = ApprovalStore()
    now = datetime.utcnow()

    record = LiveApprovalRecord(
        strategy_id="s1",
        approved_by="operator",
        approved_at=now - timedelta(days=2),
        expires_at=now - timedelta(days=1),
        notes="Expired",
    )

    store.add(record)

    assert store.get_active(strategy_id="s1", now=now) is None


def test_multiple_active_approvals_raises():
    store = ApprovalStore()
    now = datetime.utcnow()

    r1 = LiveApprovalRecord(
        strategy_id="s1",
        approved_by="op1",
        approved_at=now - timedelta(minutes=5),
        expires_at=now + timedelta(minutes=5),
        notes="A",
    )

    r2 = LiveApprovalRecord(
        strategy_id="s1",
        approved_by="op2",
        approved_at=now - timedelta(minutes=2),
        expires_at=now + timedelta(minutes=10),
        notes="B",
    )

    store.add(r1)
    store.add(r2)

    with pytest.raises(RuntimeError):
        store.get_active(strategy_id="s1", now=now)
