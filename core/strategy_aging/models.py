from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from datetime import datetime


class StrategyLifecycleState(Enum):
    YOUNG = "young"
    MATURE = "mature"
    STALE = "stale"
    ZOMBIE = "zombie"


@dataclass(frozen=True)
class StrategyAgingSignal:
    strategy_id: str
    state: StrategyLifecycleState
    age_days: int
    inactivity_days: int
    decay_score: float


@dataclass(frozen=True)
class StrategyLifecycleMemory:
    strategy_id: str
    historical_states: Tuple[StrategyLifecycleState, ...]
    first_seen: datetime
    last_updated: datetime


@dataclass(frozen=True)
class StrategyLifecycleSnapshot:
    strategy_id: str
    aging_signal: StrategyAgingSignal
    memory: StrategyLifecycleMemory
    snapshot_version: str
    generated_at: datetime
