from datetime import datetime, timedelta
from modules.governance.approval_store import ApprovalStore
from modules.governance.approval import ApprovalService


def test_approval_store_valid():
    store = ApprovalStore()
    svc = ApprovalService()

    record = svc.approve(
        "s1", "admin", "approved", ttl_hours=1
    )
    store.save(record)

    assert store.is_approved("s1", datetime.utcnow())


def test_approval_expired():
    store = ApprovalStore()
    svc = ApprovalService()

    record = svc.approve(
        "s1", "admin", "approved", ttl_hours=0
    )
    store.save(record)

    future = datetime.utcnow() + timedelta(hours=1)
    assert not store.is_approved("s1", future)
