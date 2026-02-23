from .conftest import get_events


def test_shadow_live_boot_is_safe_and_observable(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 21.1 — SHADOW LIVE BOOT SAFETY

    Invariant:
    • System may start with or without broker connectivity
    • MUST NOT crash
    • MUST remain observable
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)

    # Observable surface must exist
    assert isinstance(events, list)

    # No unsafe execution
    event_types = {e.event_type for e in events}
    assert "ORDER_EXECUTED" not in event_types
    assert "CAPITAL_MOVED" not in event_types
