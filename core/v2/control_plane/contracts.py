from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class KillSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class KillAction(str, Enum):
    HALT = "HALT"
    THROTTLE = "THROTTLE"
    CONTINUE = "CONTINUE"


class KillScope(str, Enum):
    GLOBAL = "GLOBAL"
    SYSTEM = "SYSTEM"
    STRATEGY = "STRATEGY"


@dataclass(frozen=True)
class KillSignal:
    source: str
    severity: KillSeverity
    action: KillAction
    scope: KillScope
    reason: str


@dataclass(frozen=True)
class KillDecision:
    allowed: bool
    action: KillAction
    scope: KillScope
    reason: str
    triggered_by: Optional[str] = None
