from core.explainability.timeline.events import NarrativeEvent
from core.explainability.timebox.timebox import TimeBoxedExplanation


def test_timebox_filters_and_orders_events():
    events = [
        NarrativeEvent("2026-01-02T08:59:59", "risk", "Pre-window", {}),
        NarrativeEvent("2026-01-02T09:00:00", "risk", "Risk approved", {}),
        NarrativeEvent("2026-01-02T09:30:00", "execution", "Trade executed", {}),
        NarrativeEvent("2026-01-02T10:00:00", "governance", "Governance check", {}),
        NarrativeEvent("2026-01-02T10:00:01", "risk", "Post-window", {}),
    ]

    box = TimeBoxedExplanation(
        events=events,
        start_time="2026-01-02T09:00:00",
        end_time="2026-01-02T10:00:00",
    )

    boxed = box.events()

    assert len(boxed) == 3
    assert boxed[0].description == "Risk approved"
    assert boxed[1].description == "Trade executed"
    assert boxed[2].description == "Governance check"
