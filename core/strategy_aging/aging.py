from datetime import datetime
from .models import StrategyAgingSignal, StrategyLifecycleState


def build_aging_signal(
    *,
    strategy_id: str,
    first_seen: datetime,
    last_activity: datetime,
    now: datetime,
    decay_score: float,
) -> StrategyAgingSignal:
    age_days = (now - first_seen).days
    inactivity_days = (now - last_activity).days

    if inactivity_days < 30:
        state = StrategyLifecycleState.YOUNG
    elif inactivity_days < 90:
        state = StrategyLifecycleState.MATURE
    elif inactivity_days < 180:
        state = StrategyLifecycleState.STALE
    else:
        state = StrategyLifecycleState.ZOMBIE

    return StrategyAgingSignal(
        strategy_id=strategy_id,
        state=state,
        age_days=age_days,
        inactivity_days=inactivity_days,
        decay_score=decay_score,
    )
