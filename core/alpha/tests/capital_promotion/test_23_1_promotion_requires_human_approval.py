from .conftest import get_events


def test_capital_promotion_requires_human_approval(
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 23.1 — HUMAN GATE REQUIRED

    Invariant:
    • Capital cannot be promoted without
      explicit human approval evidence
    """

    deterministic_replay.replay(ticks=[], regime_events=[])

    events = get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    forbidden = {
        "CAPITAL_PROMOTED",
        "CAPITAL_ARMED_FOR_EXECUTION",
    }

    assert forbidden.isdisjoint(event_types), (
        "Capital must not promote without human approval"
    )
