from .conftest import get_events


def test_race_conditions_do_not_escalate_authority(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 23.5.4 — RACE CONDITION DEFENSE

    Invariant:
    • Concurrent authority signals must never escalate capital
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    assert "CAPITAL_PROMOTED" not in event_types
