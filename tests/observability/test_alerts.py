from datetime import datetime
from qaai_system.observability import (
    AlertRule,
    AlertEngine,
    ObservabilityEvent,
)


def test_alert_engine_triggers_rule():
    rule = AlertRule(
        name="rollback_alert",
        condition=lambda e: e.event_type == "rollback.triggered",
    )

    engine = AlertEngine([rule])

    event = ObservabilityEvent(
        event_type="rollback.triggered",
        source="E3.5",
        model_id="m1",
        payload={},
        timestamp=datetime.utcnow(),
    )

    alerts = engine.evaluate(event)

    assert alerts == ["rollback_alert"]
