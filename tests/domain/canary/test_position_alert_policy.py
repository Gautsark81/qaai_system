from domain.canary.position_alert_policy import PositionAlertPolicy


def test_position_alert_policy():
    assert PositionAlertPolicy.should_alert(False) is True
    assert PositionAlertPolicy.should_alert(True) is False
