from datetime import datetime
from core.operator.operator_event import OperatorEvent, OperatorEventType
from core.operator.operator_memory_store import OperatorMemoryStore


def test_append_only_behavior():
    store = OperatorMemoryStore()

    event1 = OperatorEvent(
        operator_id="op1",
        event_type=OperatorEventType.APPROVAL,
        timestamp=datetime.utcnow(),
        context="approved strategy",
    )

    store.append(event1)

    events = store.all_events()
    assert len(events) == 1
    assert events[0] == event1


def test_events_filtered_by_operator():
    store = OperatorMemoryStore()

    store.append(
        OperatorEvent("op1", OperatorEventType.OVERRIDE, datetime.utcnow(), "x")
    )
    store.append(
        OperatorEvent("op2", OperatorEventType.APPROVAL, datetime.utcnow(), "y")
    )

    op1_events = store.events_for_operator("op1")
    assert len(op1_events) == 1
    assert op1_events[0].operator_id == "op1"
