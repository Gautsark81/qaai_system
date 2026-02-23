from .conftest import get_events


def test_capital_is_disarmed_by_default(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 22.1 — DEFAULT CAPITAL STATE

    Invariant:
    • System boots with capital DISARMED
    • No implicit arming
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    assert "CAPITAL_ARMED" not in event_types
    assert "CAPITAL_MOVED" not in event_types
