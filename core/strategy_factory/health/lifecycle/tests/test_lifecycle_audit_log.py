from datetime import datetime, timezone

from core.strategy_factory.health.lifecycle.lifecycle_audit_log import (
    LifecycleAuditEvent,
    LifecycleAuditLog,
)
from core.strategy_factory.health.lifecycle.strategy_lifecycle_controller import (
    StrategyLifecycleAction,
)


def utc_now():
    return datetime.now(timezone.utc)


def test_event_is_advisory_only_and_immutable():
    event = LifecycleAuditEvent(
        strategy_id="s1",
        previous_action=None,
        current_action=StrategyLifecycleAction.PROMOTE,
        timestamp=utc_now(),
        reasons=["healthy performance"],
    )

    assert event.advisory_only is True
    assert event.source == "StrategyLifecycleController"


def test_event_id_is_deterministic():
    ts = utc_now()

    e1 = LifecycleAuditEvent(
        strategy_id="s1",
        previous_action=None,
        current_action=StrategyLifecycleAction.PROMOTE,
        timestamp=ts,
        reasons=["healthy"],
    )

    e2 = LifecycleAuditEvent(
        strategy_id="s1",
        previous_action=None,
        current_action=StrategyLifecycleAction.PROMOTE,
        timestamp=ts,
        reasons=["healthy"],
    )

    assert e1.event_id == e2.event_id


def test_audit_log_appends_only_on_change():
    log = LifecycleAuditLog()

    log.record(
        strategy_id="s1",
        previous_action=None,
        current_action=StrategyLifecycleAction.HOLD,
        reasons=["initial"],
    )

    log.record(
        strategy_id="s1",
        previous_action=StrategyLifecycleAction.HOLD,
        current_action=StrategyLifecycleAction.HOLD,
        reasons=["no change"],
    )

    log.record(
        strategy_id="s1",
        previous_action=StrategyLifecycleAction.HOLD,
        current_action=StrategyLifecycleAction.PROMOTE,
        reasons=["improved health"],
    )

    events = log.events_for_strategy("s1")

    assert len(events) == 2
    assert events[0].current_action == StrategyLifecycleAction.HOLD
    assert events[1].current_action == StrategyLifecycleAction.PROMOTE


def test_events_are_ordered_and_replayable():
    log = LifecycleAuditLog()

    log.record(
        strategy_id="a",
        previous_action=None,
        current_action=StrategyLifecycleAction.WATCH,
        reasons=["degraded"],
    )
    log.record(
        strategy_id="b",
        previous_action=None,
        current_action=StrategyLifecycleAction.DEMOTE,
        reasons=["dying"],
    )

    events = log.all_events()

    assert [e.strategy_id for e in events] == ["a", "b"]
