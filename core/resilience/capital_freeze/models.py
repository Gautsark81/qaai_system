# core/resilience/capital_freeze/models.py
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class CapitalControlAction(str, Enum):
    NONE = "none"
    THROTTLE_NEW_TRADES = "throttle_new_trades"
    FREEZE_NEW_TRADES = "freeze_new_trades"
    FULL_SYSTEM_FREEZE = "full_system_freeze"


@dataclass(frozen=True)
class CapitalFreezeDecision:
    action: CapitalControlAction
    severity: float
    reason: str
    evidence: Dict[str, Any]
