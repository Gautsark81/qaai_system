from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class StrategySnapshot:
    """
    Immutable dashboard-safe strategy projection.
    """

    dna: str
    name: str
    alpha_stream: str
    state: str

    execution_status: Optional[str]
    ssr: Optional[float]
    confidence: Optional[float]

    last_updated: datetime
