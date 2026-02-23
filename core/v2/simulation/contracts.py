from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class LifecycleDecision(str, Enum):
    CONTINUE = "CONTINUE"
    PAUSE = "PAUSE"
    KILL = "KILL"


@dataclass(frozen=True)
class CapitalSnapshot:
    starting_capital: float
    ending_capital: float
    max_drawdown: float
    pnl: float


@dataclass(frozen=True)
class LifecycleOutcome:
    decision: LifecycleDecision
    reason: str
