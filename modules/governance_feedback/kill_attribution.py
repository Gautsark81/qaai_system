from dataclasses import dataclass
from enum import Enum


class KillReason(str, Enum):
    DRAWDOWN = "DRAWDOWN"
    SSR_DECAY = "SSR_DECAY"
    ABSOLUTE_LOSS = "ABSOLUTE_LOSS"
    MANUAL = "MANUAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class KillAttribution:
    strategy_id: str
    reason: KillReason
    details: str
