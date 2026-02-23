from datetime import datetime, timedelta

from core.lifecycle.contracts.snapshot import LifecycleState
from core.lifecycle.contracts.event import LifecycleEvent
from core.lifecycle.contracts.enums import TransitionReason
from core.observability.lifecycle.churn_signals import (
    LifecycleChurnSignals,
)


def test_detects_state_oscillation():
    now = datetime.utcnow()

    events = [
        LifecycleEvent(
            strategy_id="s1",
            from_state=LifecycleState.PAPER,
            to_state=LifecycleState.DEGRADED,
            reason=TransitionReason.HEALTH_DEGRADED,
            as_of=now - timedelta(days=5),
        ),
        LifecycleEvent(
            strategy_id="s1",
            from_state=LifecycleState.DEGRADED,
            to_state=LifecycleState.PAPER,
            reason=TransitionReason.SSR_STRONG,
            as_of=now - timedelta(days=3),
        ),
        LifecycleEvent(
            strategy_id="s1",
            from_state=LifecycleState.PAPER,
            to_state=LifecycleState.DEGRADED,
            reason=TransitionReason.HEALTH_DEGRADED,
            as_of=now - timedelta(days=1),
        ),
    ]

    signals = LifecycleChurnSignals.from_events(
        events=events,
        max_allowed_cycles=1,
    )

    assert "EXCESSIVE_STATE_CHURN" in signals.flags


def test_no_churn_when_stable():
    now = datetime.utcnow()

    events = [
        LifecycleEvent(
            strategy_id="s2",
            from_state=LifecycleState.CANDIDATE,
            to_state=LifecycleState.PAPER,
            reason=TransitionReason.TIME_IN_STATE,
            as_of=now - timedelta(days=10),
        ),
        LifecycleEvent(
            strategy_id="s2",
            from_state=LifecycleState.PAPER,
            to_state=LifecycleState.LIVE,
            reason=TransitionReason.SSR_STRONG,
            as_of=now - timedelta(days=2),
        ),
    ]

    signals = LifecycleChurnSignals.from_events(
        events=events,
        max_allowed_cycles=1,
    )

    assert signals.flags == []
