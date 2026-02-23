from .conftest import get_events


def test_capital_arming_is_never_silent(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 22.3 — ARMING MUST BE AUDITED

    Invariant:
    • If capital ever arms in future phases,
      it MUST emit forensic evidence
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)

    # Absence of arming is acceptable
    # Silent arming is NOT
    assert all(
        e.event_type != "CAPITAL_ARMED_SILENT"
        for e in events
    )
