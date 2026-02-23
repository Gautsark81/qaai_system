from dataclasses import dataclass


@dataclass(frozen=True)
class PositionReconciliationResult:
    symbol: str
    system_qty: int
    broker_qty: int
    delta_qty: int
    matched: bool
