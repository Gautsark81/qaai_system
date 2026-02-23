from datetime import datetime
from domain.observability.system_health import SystemHealthSnapshot


def test_system_health_snapshot_fields():
    snap = SystemHealthSnapshot(
        timestamp=datetime.utcnow(),
        components={"data": "OK", "execution": "OK"},
        warnings=0,
        errors=0,
    )
    assert snap.errors == 0
