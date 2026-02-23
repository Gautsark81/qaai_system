from dataclasses import dataclass


@dataclass(frozen=True)
class ReconciliationResult:
    intent_id: str
    authorized_capital: float
    broker_executed_capital: float
    delta: float               # broker - authorized
    within_tolerance: bool
