from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class CapitalRequest:
    strategy_id: str
    requested_amount: float
    timestamp: datetime


@dataclass(frozen=True)
class CoordinationDecision:
    granted: Dict[str, float]
    remaining_capital: float
    explanations: Dict[str, str]
