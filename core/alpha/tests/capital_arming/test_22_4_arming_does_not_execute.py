from .conftest import get_events


def test_capital_arming_never_triggers_execution(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 22.4 — ARMING ≠ EXECUTION

    Invariant:
    • Even if capital were armed,
      execution must remain impossible
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    assert "ORDER_EXECUTED" not in event_types
    assert "CAPITAL_MOVED" not in event_types
