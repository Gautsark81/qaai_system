from datetime import datetime, timedelta

from core.lifecycle.contracts.snapshot import LifecycleState
from core.lifecycle.contracts.event import LifecycleEvent
from core.lifecycle.contracts.enums import TransitionReason
from core.observability.lifecycle.stagnation_signals import (
    LifecycleStagnationSignals,
)


def test_detects_stagnation_in_paper():
    now = datetime.utcnow()

    events = [
        LifecycleEvent(
            strategy_id="s1",
            from_state=LifecycleState.CANDIDATE,
            to_state=LifecycleState.PAPER,
            reason=TransitionReason.TIME_IN_STATE,
            as_of=now - timedelta(days=20),
        ),
    ]

    signals = LifecycleStagnationSignals.from_events(
        events=events,
        now=now,
        max_days_in_state={
            LifecycleState.PAPER: 14,
        },
    )

    assert "STAGNANT_IN_PAPER" in signals.flags


def test_no_stagnation_when_within_limits():
    now = datetime.utcnow()

    events = [
        LifecycleEvent(
            strategy_id="s2",
            from_state=LifecycleState.CANDIDATE,
            to_state=LifecycleState.PAPER,
            reason=TransitionReason.TIME_IN_STATE,
            as_of=now - timedelta(days=5),
        ),
    ]

    signals = LifecycleStagnationSignals.from_events(
        events=events,
        now=now,
        max_days_in_state={
            LifecycleState.PAPER: 14,
        },
    )

    assert signals.flags == []
