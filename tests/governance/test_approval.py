from modules.governance.approval import ApprovalService, ApprovalDecision


def test_approval_expires():
    svc = ApprovalService()
    record = svc.approve("s1", "admin", "Looks good", ttl_hours=24)

    assert record.decision == ApprovalDecision.APPROVED
    assert record.expires_at is not None


def test_rejection_no_expiry():
    svc = ApprovalService()
    record = svc.reject("s1", "admin", "Too risky")

    assert record.decision == ApprovalDecision.REJECTED
    assert record.expires_at is None
