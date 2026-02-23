from enum import Enum
from dataclasses import dataclass
from .metrics import StrategyMetrics


class StrategyHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class HealthReport:
    health: StrategyHealth
    reason: str


class StrategyHealthEvaluator:
    def evaluate(self, metrics: StrategyMetrics) -> HealthReport:
        if metrics.total_trades < 30:
            return HealthReport(
                StrategyHealth.DEGRADED,
                "Insufficient trade sample",
            )

        if metrics.net_pnl < 0:
            return HealthReport(
                StrategyHealth.FAILED,
                "Negative net PnL",
            )

        return HealthReport(
            StrategyHealth.HEALTHY,
            "Strategy operating within expected parameters",
        )
