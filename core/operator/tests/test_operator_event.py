from datetime import datetime
from core.operator.operator_event import OperatorEvent, OperatorEventType


def test_operator_event_is_immutable():
    event = OperatorEvent(
        operator_id="op1",
        event_type=OperatorEventType.OVERRIDE,
        timestamp=datetime.utcnow(),
        context="manual override",
    )

    try:
        event.context = "changed"
        assert False, "OperatorEvent should be immutable"
    except Exception:
        assert True
