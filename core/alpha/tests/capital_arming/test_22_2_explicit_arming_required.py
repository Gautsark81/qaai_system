from .conftest import get_events


def test_capital_requires_explicit_arming_signal(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 22.2 — EXPLICIT ARMING REQUIRED

    Invariant:
    • Capital cannot arm implicitly
    • Absence of arming evidence == safe
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    forbidden = {
        "CAPITAL_ARMED",
        "CAPITAL_READY",
        "CAPITAL_AVAILABLE",
    }

    assert forbidden.isdisjoint(event_types), (
        "Capital must never arm implicitly"
    )
