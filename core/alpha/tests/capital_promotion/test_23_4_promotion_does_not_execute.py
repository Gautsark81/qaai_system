from .conftest import get_events


def test_capital_promotion_never_triggers_execution(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 23.4 — PROMOTION DOES NOT EXECUTE

    Invariant:
    • Promotion authorizes execution
      but does not cause execution
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    assert "ORDER_EXECUTED" not in event_types
    assert "CAPITAL_MOVED" not in event_types
