from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OperatorAction:
    operator_id: str
    action: str          # VIEW / APPROVE / PAUSE / KILL
    target: str          # strategy_id / system
    reason: str
    timestamp: datetime
