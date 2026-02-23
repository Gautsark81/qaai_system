from .conftest import get_events


def test_shadow_live_does_not_silently_assume_time_authority(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 21.3 — TIME AUTHORITY SAFETY

    Invariant:
    • System must NOT silently assume broker time
    • Absence of drift evidence is acceptable
    • Silent execution is NOT
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    # Allowed: no drift measurement yet
    # Forbidden: unsafe behavior
    assert "ORDER_EXECUTED" not in event_types
    assert "CAPITAL_MOVED" not in event_types
