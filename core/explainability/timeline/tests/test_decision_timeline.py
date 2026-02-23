from core.explainability.timeline.events import NarrativeEvent
from core.explainability.timeline.timeline import NarrativeTimeline


def test_timeline_orders_events_deterministically():
    events = [
        NarrativeEvent("2026-01-02T10:00:00", "execution", "Executed trade", {}),
        NarrativeEvent("2026-01-02T09:00:00", "risk", "Risk approved", {}),
        NarrativeEvent("2026-01-02T10:00:00", "governance", "Governance check", {}),
    ]

    timeline = NarrativeTimeline(events)
    ordered = timeline.all_events()

    assert ordered[0].category == "risk"
    assert ordered[1].category == "execution"
    assert ordered[2].category == "governance"


def test_filter_by_category():
    events = [
        NarrativeEvent("2026-01-02T09:00:00", "risk", "Risk approved", {}),
        NarrativeEvent("2026-01-02T10:00:00", "execution", "Executed trade", {}),
    ]

    timeline = NarrativeTimeline(events)
    risk_events = timeline.filter_by_category("risk")

    assert len(risk_events) == 1
    assert risk_events[0].category == "risk"
