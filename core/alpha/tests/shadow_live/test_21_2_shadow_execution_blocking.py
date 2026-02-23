from .conftest import get_events


def test_shadow_mode_never_executes_orders(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 21.2 — SHADOW EXECUTION ABSOLUTE BLOCK

    Invariant:
    • No execution
    • No capital movement
    • No broker side-effects
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    forbidden = {
        "ORDER_EXECUTED",
        "ORDER_PLACED",
        "CAPITAL_MOVED",
        "BROKER_FILL_RECEIVED",
    }

    assert forbidden.isdisjoint(event_types), (
        "Shadow Live MUST NOT execute or move capital"
    )
