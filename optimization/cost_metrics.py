from dataclasses import dataclass


@dataclass(frozen=True)
class CostMetrics:
    brokerage_paid: float
    slippage_cost: float
