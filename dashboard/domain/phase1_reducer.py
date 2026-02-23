from dashboard.domain.phase1_state import Phase1SystemState
from dashboard.domain.invariants import Phase1InvariantViolation


def reduce_event(
    state: Phase1SystemState,
    event: dict,
) -> Phase1SystemState:
    """
    Phase-1 reducer.

    Rules:
    - Pure
    - Deterministic
    - Returns NEW state
    """

    if not isinstance(event, dict):
        raise Phase1InvariantViolation("Event must be a dict")

    event_type = event.get("event_type")

    # --------------------------------------------------
    # Phase-1 supported events
    # --------------------------------------------------
    if event_type == "ExecutionIntentCreated":
        return Phase1SystemState(
            **{
                **state.__dict__,
                "intent_count": state.intent_count + 1,
            }
        )

    # Unknown events are ignored in Phase-1
    return state
