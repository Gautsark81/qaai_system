# modules/execution/plan.py

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ExecutionPlan:
    plan_id: str
    strategy_id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    quantity: int
    order_type: Literal["MARKET"]
    reason: str
