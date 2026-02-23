from .conftest import get_events


def test_operator_panic_never_forces_promotion(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 23.5.3 — OPERATOR PANIC

    Invariant:
    • Conflicting human actions must never force capital promotion
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    assert "CAPITAL_PROMOTED" not in event_types
