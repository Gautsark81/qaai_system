from .conftest import get_events


def test_shadow_reconciliation_has_zero_side_effects(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 21.4 — RECONCILIATION SAFETY

    Invariant:
    • Reconciliation may be absent
    • But must NEVER move capital
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    assert "CAPITAL_MOVED" not in event_types
    assert "ORDER_EXECUTED" not in event_types
