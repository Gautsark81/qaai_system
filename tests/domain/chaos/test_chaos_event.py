from datetime import datetime
from domain.chaos.chaos_event import ChaosEvent


def test_chaos_event_fields():
    e = ChaosEvent(
        event_type="BROKER_DOWN",
        source="Dhan",
        occurred_at=datetime.utcnow(),
        details="No heartbeat",
    )
    assert e.event_type == "BROKER_DOWN"
