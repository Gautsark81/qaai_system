from datetime import datetime
from typing import Tuple
from .models import (
    StrategyLifecycleMemory,
    StrategyLifecycleState,
)


def build_lifecycle_memory(
    *,
    strategy_id: str,
    prior_states: Tuple[StrategyLifecycleState, ...],
    new_state: StrategyLifecycleState,
    first_seen: datetime,
    now: datetime,
) -> StrategyLifecycleMemory:
    updated = prior_states + (new_state,)

    return StrategyLifecycleMemory(
        strategy_id=strategy_id,
        historical_states=updated,
        first_seen=first_seen,
        last_updated=now,
    )
