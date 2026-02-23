from datetime import datetime, timezone

from core.strategy_factory.health.death_event_store import DeathEventStore
from core.strategy_factory.health.death_attribution import DeathAttribution
from core.strategy_factory.health.death_reason import DeathReason


def test_death_event_store_starts_empty():
    store = DeathEventStore()
    assert store.all_events() == []


def test_death_event_store_appends_event():
    store = DeathEventStore()

    event = DeathAttribution(
        strategy_id="s1",
        reason=DeathReason.MAX_DRAWDOWN,
        timestamp=datetime.now(timezone.utc),
        triggered_by="health_engine",
        metrics={"drawdown": -0.22},
    )

    store.record(event)

    events = store.all_events()
    assert len(events) == 1
    assert events[0] is event


def test_death_event_store_is_append_only():
    store = DeathEventStore()

    e1 = DeathAttribution(
        strategy_id="s1",
        reason=DeathReason.SSR_FAILURE,
        timestamp=datetime.now(timezone.utc),
        triggered_by="fitness_monitor",
        metrics={"ssr": 0.3},
    )

    e2 = DeathAttribution(
        strategy_id="s2",
        reason=DeathReason.OPERATOR_KILL,
        timestamp=datetime.now(timezone.utc),
        triggered_by="operator",
        metrics={},
    )

    store.record(e1)
    store.record(e2)

    events = store.all_events()
    assert events == [e1, e2]


def test_death_event_store_returns_copy():
    store = DeathEventStore()

    event = DeathAttribution(
        strategy_id="s1",
        reason=DeathReason.SYSTEM_GUARDRAIL,
        timestamp=datetime.now(timezone.utc),
        triggered_by="risk_engine",
        metrics={},
    )

    store.record(event)

    events = store.all_events()
    events.clear()

    # Internal store must remain intact
    assert len(store.all_events()) == 1
