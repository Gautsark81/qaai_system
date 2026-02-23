from datetime import datetime
from core.operator.operator_event import OperatorEvent, OperatorEventType
from core.operator.abuse_detection import detect_override_abuse


def _event(op, et):
    return OperatorEvent(op, et, datetime.utcnow(), "x")


def test_no_abuse_for_low_event_count():
    events = [
        _event("op1", OperatorEventType.OVERRIDE),
        _event("op1", OperatorEventType.APPROVAL),
    ]

    assert detect_override_abuse("op1", events) is None


def test_no_abuse_for_normal_behavior():
    events = [
        _event("op1", OperatorEventType.APPROVAL),
        _event("op1", OperatorEventType.OVERRIDE),
        _event("op1", OperatorEventType.APPROVAL),
        _event("op1", OperatorEventType.INTERVENTION),
        _event("op1", OperatorEventType.APPROVAL),
    ]

    assert detect_override_abuse("op1", events) is None


def test_abuse_detected_by_override_ratio():
    events = [
        _event("op1", OperatorEventType.OVERRIDE),
        _event("op1", OperatorEventType.OVERRIDE),
        _event("op1", OperatorEventType.OVERRIDE),
        _event("op1", OperatorEventType.APPROVAL),
        _event("op1", OperatorEventType.OVERRIDE),
    ]

    signal = detect_override_abuse("op1", events)

    assert signal is not None
    assert signal.operator_id == "op1"
    assert signal.confidence > 0.6
    assert len(signal.evidence_event_ids) >= 3


def test_abuse_detected_by_consecutive_streak():
    events = [
        _event("op1", OperatorEventType.APPROVAL),
        _event("op1", OperatorEventType.OVERRIDE),
        _event("op1", OperatorEventType.OVERRIDE),
        _event("op1", OperatorEventType.OVERRIDE),
        _event("op1", OperatorEventType.APPROVAL),
    ]

    signal = detect_override_abuse("op1", events)

    assert signal is not None
    assert signal.confidence >= 0.2
