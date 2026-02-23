from dataclasses import dataclass
from typing import Optional
from .health_score import StrategyHealthScore


@dataclass(frozen=True)
class StrategyDiagnosticSnapshot:
    """
    Immutable advisory snapshot describing
    current strategy health.

    Used for:
    - dashboards
    - monitoring
    - intelligence context
    """

    timestamp: int
    strategy_id: str
    health: StrategyHealthScore
    notes: Optional[str] = None
