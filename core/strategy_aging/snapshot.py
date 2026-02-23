import hashlib
import json
from datetime import datetime

from .models import (
    StrategyLifecycleSnapshot,
    StrategyAgingSignal,
    StrategyLifecycleMemory,
)


def _version_key(
    signal: StrategyAgingSignal,
    memory: StrategyLifecycleMemory,
) -> str:
    payload = {
        "strategy_id": signal.strategy_id,
        "state": signal.state.value,
        "age_days": signal.age_days,
        "inactivity_days": signal.inactivity_days,
        "decay_score": signal.decay_score,
        "history": tuple(s.value for s in memory.historical_states),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def build_strategy_lifecycle_snapshot(
    *,
    aging_signal: StrategyAgingSignal,
    memory: StrategyLifecycleMemory,
    now: datetime,
) -> StrategyLifecycleSnapshot:
    return StrategyLifecycleSnapshot(
        strategy_id=aging_signal.strategy_id,
        aging_signal=aging_signal,
        memory=memory,
        snapshot_version=_version_key(aging_signal, memory),
        generated_at=now,
    )
