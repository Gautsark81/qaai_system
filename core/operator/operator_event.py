# core/operator/operator_event.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class OperatorEventType(str, Enum):
    OVERRIDE = "override"
    APPROVAL = "approval"
    ABORT = "abort"
    INTERVENTION = "intervention"
    COMMENT = "comment"


@dataclass(frozen=True)
class OperatorEvent:
    operator_id: str
    event_type: OperatorEventType
    timestamp: datetime
    context: str
    related_strategy_id: Optional[str] = None
    related_trade_id: Optional[str] = None
