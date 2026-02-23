from runbook.recovery_checklist import recovery_checklist


def test_recovery_checklist_complete():
    steps = recovery_checklist()
    assert "broker_reconciled" in steps
