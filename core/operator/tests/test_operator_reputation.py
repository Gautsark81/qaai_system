from datetime import datetime
from core.operator.operator_event import OperatorEvent, OperatorEventType
from core.operator.reputation import compute_reputation


def test_reputation_computation_is_deterministic():
    events = [
        OperatorEvent("op1", OperatorEventType.OVERRIDE, datetime.utcnow(), "a"),
        OperatorEvent("op1", OperatorEventType.APPROVAL, datetime.utcnow(), "b"),
        OperatorEvent("op1", OperatorEventType.OVERRIDE, datetime.utcnow(), "c"),
    ]

    rep = compute_reputation("op1", events)

    assert rep.total_events == 3
    assert rep.override_count == 2
    assert rep.approval_count == 1
    assert rep.override_ratio == 2 / 3
