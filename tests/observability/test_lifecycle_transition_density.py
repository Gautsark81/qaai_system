from datetime import datetime, timedelta

from core.lifecycle.contracts.snapshot import LifecycleState
from core.lifecycle.contracts.event import LifecycleEvent
from core.lifecycle.contracts.enums import TransitionReason
from core.observability.lifecycle.transition_density import (
    LifecycleTransitionDensity,
)


def test_transition_density_aggregates_correctly():
    now = datetime.utcnow()

    events = [
        LifecycleEvent(
            strategy_id="s1",
            from_state=LifecycleState.CANDIDATE,
            to_state=LifecycleState.PAPER,
            reason=TransitionReason.TIME_IN_STATE,
            as_of=now - timedelta(days=2),
        ),
        LifecycleEvent(
            strategy_id="s1",
            from_state=LifecycleState.PAPER,
            to_state=LifecycleState.LIVE,
            reason=TransitionReason.SSR_STRONG,
            as_of=now - timedelta(days=1),
        ),
    ]

    report = LifecycleTransitionDensity.from_events(events)

    assert report.total_transitions == 2
    assert report.by_state[LifecycleState.CANDIDATE] == 1
    assert report.by_state[LifecycleState.PAPER] == 1
    assert report.by_reason[TransitionReason.TIME_IN_STATE] == 1
    assert report.by_reason[TransitionReason.SSR_STRONG] == 1
    assert report.first_event_at < report.last_event_at
