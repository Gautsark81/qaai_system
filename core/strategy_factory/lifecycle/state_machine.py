from enum import Enum
from core.strategy_factory.exceptions import IllegalLifecycleTransition


class LifecycleState(Enum):
    CREATED = "CREATED"
    SCREENED = "SCREENED"
    WATCHLISTED = "WATCHLISTED"
    PAPER = "PAPER"
    CANDIDATE = "CANDIDATE"
    LIVE = "LIVE"
    FROZEN = "FROZEN"
    RETIRED = "RETIRED"
    KILLED = "KILLED"


_ALLOWED_TRANSITIONS = {
    LifecycleState.CREATED: {LifecycleState.SCREENED},
    LifecycleState.SCREENED: {LifecycleState.WATCHLISTED, LifecycleState.FROZEN},
    LifecycleState.WATCHLISTED: {LifecycleState.PAPER, LifecycleState.FROZEN},
    LifecycleState.PAPER: {LifecycleState.CANDIDATE, LifecycleState.FROZEN},
    LifecycleState.CANDIDATE: {LifecycleState.LIVE, LifecycleState.FROZEN},
    LifecycleState.LIVE: {LifecycleState.FROZEN, LifecycleState.RETIRED},
    LifecycleState.FROZEN: {LifecycleState.PAPER, LifecycleState.RETIRED},
    LifecycleState.RETIRED: set(),
    LifecycleState.KILLED: set(),
}


def validate_transition(from_state: LifecycleState, to_state: LifecycleState) -> None:
    allowed = _ALLOWED_TRANSITIONS.get(from_state, set())
    if to_state not in allowed:
        raise IllegalLifecycleTransition(
            f"Illegal Phase-9 transition: {from_state.value} → {to_state.value}"
        )
