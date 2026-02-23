# core/strategy_factory/lifecycle/contracts.py

from enum import Enum
from typing import Dict, Set


# ======================================================
# 🔒 STRATEGY LIFECYCLE STATE (CANONICAL)
# ======================================================

class StrategyLifecycleState(str, Enum):
    RESEARCH = "RESEARCH"
    BACKTESTED = "BACKTESTED"
    PAPER = "PAPER"
    LIVE = "LIVE"
    DEGRADED = "DEGRADED"
    RETIRED = "RETIRED"


# ======================================================
# 🔁 ALLOWED TRANSITIONS (HARD GOVERNANCE)
# ======================================================

_ALLOWED_TRANSITIONS: Dict[
    StrategyLifecycleState,
    Set[StrategyLifecycleState],
] = {
    StrategyLifecycleState.RESEARCH: {
        StrategyLifecycleState.BACKTESTED,
    },
    StrategyLifecycleState.BACKTESTED: {
        StrategyLifecycleState.PAPER,
    },
    StrategyLifecycleState.PAPER: {
        StrategyLifecycleState.LIVE,
    },
    StrategyLifecycleState.LIVE: {
        StrategyLifecycleState.DEGRADED,
        StrategyLifecycleState.RETIRED,
    },
    StrategyLifecycleState.DEGRADED: {
        StrategyLifecycleState.PAPER,
        StrategyLifecycleState.RETIRED,
    },
    StrategyLifecycleState.RETIRED: set(),
}


# ======================================================
# ✅ PURE VALIDATION FUNCTION
# ======================================================

def is_transition_allowed(
    src: StrategyLifecycleState,
    dst: StrategyLifecycleState,
) -> bool:
    """
    Check whether a lifecycle transition is allowed.

    Rules:
    - No self-transitions
    - Only explicitly allowed edges are valid
    - Pure function (no side effects)
    """

    if src == dst:
        return False

    return dst in _ALLOWED_TRANSITIONS.get(src, set())
