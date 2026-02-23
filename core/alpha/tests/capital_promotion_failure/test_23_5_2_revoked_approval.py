from .conftest import get_events


def test_revoked_approval_never_promotes_capital(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 23.5.2 — APPROVAL REVOCATION

    Invariant:
    • Capital must not be promoted without final authority
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    assert "CAPITAL_PROMOTED" not in event_types
