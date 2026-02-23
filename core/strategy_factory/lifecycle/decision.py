from __future__ import annotations

from core.strategy_factory.lifecycle.contracts import (
    StrategyLifecycleState,
    is_transition_allowed,
)


def decide_lifecycle_transition(
    *,
    current: StrategyLifecycleState,
    requested: StrategyLifecycleState,
) -> StrategyLifecycleState:
    """
    Decide whether a lifecycle state transition is allowed.

    Pure governance decision:
    - No IO
    - No side effects
    - No evidence emission
    """

    # 1️⃣ Self-transition forbidden
    if current == requested:
        raise ValueError(
            f"Self-transition is not allowed: {current.value} → {requested.value}"
        )

    # 2️⃣ Terminal state is immutable
    if current == StrategyLifecycleState.RETIRED:
        raise ValueError(
            f"Cannot transition from terminal state: {current.value}"
        )

    # 3️⃣ Validate transition via existing rule engine
    if not is_transition_allowed(current, requested):
        raise ValueError(
            f"Invalid lifecycle transition: {current.value} → {requested.value}"
        )

    # 4️⃣ Approved transition
    return requested
