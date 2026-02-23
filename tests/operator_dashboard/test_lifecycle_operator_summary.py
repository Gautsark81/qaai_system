from datetime import datetime, timedelta

from core.lifecycle.contracts.snapshot import LifecycleState
from core.lifecycle.contracts.event import LifecycleEvent
from core.lifecycle.contracts.enums import TransitionReason
from core.operator_dashboard.lifecycle_summary import (
    LifecycleOperatorSummary,
)


def test_operator_lifecycle_summary_assembly():
    now = datetime.utcnow()

    events = [
        LifecycleEvent(
            strategy_id="s1",
            from_state=LifecycleState.CANDIDATE,
            to_state=LifecycleState.PAPER,
            reason=TransitionReason.TIME_IN_STATE,
            as_of=now - timedelta(days=10),
        ),
        LifecycleEvent(
            strategy_id="s1",
            from_state=LifecycleState.PAPER,
            to_state=LifecycleState.DEGRADED,
            reason=TransitionReason.HEALTH_DEGRADED,
            as_of=now - timedelta(days=3),
        ),
    ]

    summary = LifecycleOperatorSummary.from_events(
        strategy_id="s1",
        events=events,
        now=now,
        stagnation_flags=["STAGNANT_IN_PAPER"],
        churn_flags=[],
    )

    assert summary.strategy_id == "s1"
    assert summary.current_state == LifecycleState.DEGRADED
    assert summary.days_in_current_state == 3
    assert "STAGNANT_IN_PAPER" in summary.flags
    assert len(summary.recent_transitions) == 2
