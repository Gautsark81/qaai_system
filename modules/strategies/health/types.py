# modules/strategies/health/types.py

from dataclasses import dataclass
from enum import Enum


class StrategyState(Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class StrategyHealth:
    state: StrategyState
    failure_count: int
    last_reason: str | None
