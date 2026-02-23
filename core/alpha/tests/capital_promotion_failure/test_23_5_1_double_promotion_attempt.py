from .conftest import get_events


def test_double_capital_promotion_is_idempotent(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 23.5.1 — DOUBLE PROMOTION ATTEMPT

    Invariant:
    • Capital must never be promoted implicitly
    • Multiple attempts must not escalate authority
    """

    deterministic_replay.replay(ticks=[], regime_events=[])
    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    assert "CAPITAL_PROMOTED" not in event_types
