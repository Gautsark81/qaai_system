from datetime import datetime
from core.strategy_aging.snapshot import build_strategy_lifecycle_snapshot
from core.strategy_aging.models import (
    StrategyAgingSignal,
    StrategyLifecycleMemory,
    StrategyLifecycleState,
)


def test_snapshot_is_deterministic():
    now = datetime.utcnow()

    signal = StrategyAgingSignal(
        strategy_id="s1",
        state=StrategyLifecycleState.MATURE,
        age_days=100,
        inactivity_days=20,
        decay_score=0.2,
    )

    memory = StrategyLifecycleMemory(
        strategy_id="s1",
        historical_states=(StrategyLifecycleState.YOUNG,),
        first_seen=now,
        last_updated=now,
    )

    s1 = build_strategy_lifecycle_snapshot(
        aging_signal=signal,
        memory=memory,
        now=now,
    )
    s2 = build_strategy_lifecycle_snapshot(
        aging_signal=signal,
        memory=memory,
        now=now,
    )

    assert s1.snapshot_version == s2.snapshot_version
