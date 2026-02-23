from datetime import datetime, timedelta

from core.lifecycle.contracts.event import LifecycleEvent
from core.lifecycle.contracts.state import LifecycleState
from core.observability.lifecycle.timeline import LifecycleAuditTimeline


def test_timeline_orders_events_chronologically():
    now = datetime.utcnow()

    e1 = LifecycleEvent(
        strategy_id="s1",
        from_state=LifecycleState.CANDIDATE,
        to_state=LifecycleState.PAPER,
        reason="PROMOTION",
        as_of=now - timedelta(days=2),
    )

    e2 = LifecycleEvent(
        strategy_id="s1",
        from_state=LifecycleState.PAPER,
        to_state=LifecycleState.LIVE,
        reason="PROMOTION",
        as_of=now,
    )

    timeline = LifecycleAuditTimeline(events=[e2, e1])

    ordered = timeline.events

    assert ordered[0].as_of < ordered[1].as_of
