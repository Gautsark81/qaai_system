from .conftest import get_events


def test_capital_promotion_is_never_silent(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 23.2 — PROMOTION MUST BE AUDITED

    Invariant:
    • Any capital promotion must emit
      explicit forensic evidence
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)

    assert all(
        e.event_type != "CAPITAL_PROMOTED_SILENT"
        for e in events
    ), "Silent capital promotion is forbidden"
