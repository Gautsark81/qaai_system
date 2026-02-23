from datetime import datetime
from domain.observability.alert import Alert


def test_alert_fields():
    a = Alert("HIGH", "execution", "Duplicate blocked", datetime.utcnow())
    assert a.severity == "HIGH"
