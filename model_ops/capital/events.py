from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CapitalEventType(str, Enum):
    """
    Enumerates capital lifecycle events.
    Phase-11 defines the contract; later phases may act on them.
    """
    ALLOCATION = "allocation"
    DEALLOCATION = "deallocation"
    REBALANCE = "rebalance"
    RESET = "reset"


@dataclass(frozen=True)
class CapitalEvent:
    """
    Immutable capital event record.

    NOTE:
    Phase-11 only *emits* or *describes* events.
    No execution, mutation, or side-effects are allowed here.
    """

    event_type: CapitalEventType
    strategy_id: Optional[str]
    amount: float
    reason: str

    def __post_init__(self) -> None:
        if self.amount < 0.0:
            raise ValueError("CapitalEvent.amount must be non-negative")
