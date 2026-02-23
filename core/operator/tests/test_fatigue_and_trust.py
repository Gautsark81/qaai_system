from datetime import datetime, timedelta
from core.operator.operator_event import OperatorEvent, OperatorEventType
from core.operator.fatigue import compute_fatigue_level
from core.operator.trust_score import compute_trust_score


def _event(op, et, minutes_ago=0):
    return OperatorEvent(
        operator_id=op,
        event_type=et,
        timestamp=datetime.utcnow() - timedelta(minutes=minutes_ago),
        context="x",
    )


def test_fatigue_low_for_sparse_events():
    events = [_event("op1", OperatorEventType.APPROVAL, minutes_ago=60)]
    fatigue = compute_fatigue_level(events)
    assert fatigue == 0.0


def test_fatigue_high_for_dense_activity():
    events = [
        _event("op1", OperatorEventType.OVERRIDE, minutes_ago=i)
        for i in range(10)
    ]
    fatigue = compute_fatigue_level(events)
    assert fatigue > 0.5


def test_trust_decays_faster_under_fatigue():
    events = [
        _event("op1", OperatorEventType.OVERRIDE, minutes_ago=i)
        for i in range(10)
    ]

    score = compute_trust_score("op1", events)
    assert score.trust < 0.7
    assert score.fatigue > 0.5


def test_trust_recovers_with_clean_behavior():
    events = [
        _event("op1", OperatorEventType.OVERRIDE, minutes_ago=30),
        _event("op1", OperatorEventType.APPROVAL, minutes_ago=20),
        _event("op1", OperatorEventType.APPROVAL, minutes_ago=10),
    ]

    score = compute_trust_score("op1", events)
    assert score.trust > 0.9
