from domain.canary.reconciliation_alert_policy import ReconciliationAlertPolicy


def test_alert_policy():
    assert ReconciliationAlertPolicy.should_alert(False) is True
    assert ReconciliationAlertPolicy.should_alert(True) is False
