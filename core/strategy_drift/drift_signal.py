from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StrategyDriftSignal:
    """
    Advisory signal indicating strategy decay or regime mismatch.
    """

    strategy_id: str
    signal_type: str
    severity: str
    note: Optional[str] = None
