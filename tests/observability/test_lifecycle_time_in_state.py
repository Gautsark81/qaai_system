from datetime import datetime, timedelta

from core.lifecycle.contracts.snapshot import LifecycleState
from core.lifecycle.contracts.event import LifecycleEvent
from core.lifecycle.contracts.enums import TransitionReason
from core.observability.lifecycle.time_in_state import (
    LifecycleTimeInStateReport,
)


def test_time_in_state_computation():
    now = datetime.utcnow()

    events = [
        LifecycleEvent(
            strategy_id="s1",
            from_state=LifecycleState.CANDIDATE,
            to_state=LifecycleState.PAPER,
            reason=TransitionReason.TIME_IN_STATE,
            as_of=now - timedelta(days=5),
        ),
        LifecycleEvent(
            strategy_id="s1",
            from_state=LifecycleState.PAPER,
            to_state=LifecycleState.LIVE,
            reason=TransitionReason.SSR_STRONG,
            as_of=now - timedelta(days=2),
        ),
    ]

    report = LifecycleTimeInStateReport.from_events(events, as_of=now)

    assert report.duration_by_state[LifecycleState.CANDIDATE] == timedelta(days=3)
    assert report.duration_by_state[LifecycleState.PAPER] == timedelta(days=2)
    assert report.first_event_at < report.last_event_at
