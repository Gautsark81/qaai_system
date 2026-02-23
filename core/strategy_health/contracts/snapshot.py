from dataclasses import dataclass
from datetime import datetime
from .enums import HealthStatus
from .flags import HealthFlag
from .dimension import HealthDimensionScore


@dataclass(frozen=True)
class StrategyHealthSnapshot:
    """
    Immutable, audit-grade health snapshot for a strategy.
    """
    strategy_id: str
    as_of: datetime

    overall_score: float
    status: HealthStatus

    dimensions: dict[str, HealthDimensionScore]

    trailing_metrics: dict[str, float]
    regime_context: str
    confidence: float

    flags: list[HealthFlag]
    version: str

    def __post_init__(self):
        if not (0.0 <= self.overall_score <= 1.0):
            raise ValueError("overall_score must be in [0.0, 1.0]")

        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be in [0.0, 1.0]")
