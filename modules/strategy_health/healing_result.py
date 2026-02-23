from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class HealingResult:
    """
    Outcome of a healing attempt.
    """
    success: bool
    new_strategy_id: Optional[str]
    reason: str
