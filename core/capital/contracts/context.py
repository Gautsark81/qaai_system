from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class CapitalDecisionContext:
    """
    Immutable capital decision input contract.
    """

    strategy_id: str
    base_capital: float
    lifecycle_state: Optional[object]
    modifiers: List[object]
