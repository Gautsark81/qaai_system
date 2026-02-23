from datetime import datetime
from domain.observability.alert import Alert
from domain.observability.alert_manager import AlertManager


def test_alert_manager_stores_alert():
    mgr = AlertManager()
    mgr.raise_alert(
        Alert("CRITICAL", "risk", "Kill switch engaged", datetime.utcnow())
    )
    assert len(mgr.active()) == 1
