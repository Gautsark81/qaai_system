from .conftest import get_events


def test_capital_promotion_is_rate_limited(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 23.3 — PROMOTION COOLDOWN

    Invariant:
    • Capital cannot be promoted repeatedly
      without cooldown / stabilization window
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)

    promotions = [
        e for e in events
        if e.event_type == "CAPITAL_PROMOTED"
    ]

    assert len(promotions) <= 1, (
        "Capital promotion must be rate-limited"
    )
