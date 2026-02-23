from datetime import datetime
from qaai_system.observability import ObservabilityEvent


def test_event_creation():
    event = ObservabilityEvent(
        event_type="decay.detected",
        source="E4",
        model_id="m1",
        payload={"reason": "SharpeDecay"},
        timestamp=datetime.utcnow(),
    )

    assert event.event_type == "decay.detected"
    assert event.source == "E4"
