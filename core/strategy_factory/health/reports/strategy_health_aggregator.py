from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from core.strategy_factory.health.strategy_health_report import (
    StrategyHealthReport,
    StrategyHealthStatus,
)


_STATUS_PRIORITY = {
    StrategyHealthStatus.DEAD: 3,
    StrategyHealthStatus.DYING: 2,
    StrategyHealthStatus.DEGRADED: 1,
    StrategyHealthStatus.HEALTHY: 0,
}


@dataclass(frozen=True)
class StrategyHealthAggregator:
    """
    Advisory-only aggregation of multiple StrategyHealthReport objects.

    Characteristics:
    - Deterministic
    - Side-effect free
    - Governance-grade
    - Never executes or enforces
    """

    reports: List[StrategyHealthReport]

    advisory_only: bool = field(init=False, default=True)
    total_strategies: int = field(init=False)
    status_counts: Dict[StrategyHealthStatus, int] = field(init=False)
    overall_status: StrategyHealthStatus = field(init=False)

    dead_strategies: List[str] = field(init=False)
    dying_strategies: List[str] = field(init=False)

    promotion_pressure: bool = field(init=False)
    demotion_pressure: bool = field(init=False)

    # ----------------------------
    # Lifecycle
    # ----------------------------

    def __post_init__(self):
        self._aggregate()

    # ----------------------------
    # Core Aggregation
    # ----------------------------

    def _aggregate(self) -> None:
        total = len(self.reports)

        counts = {
            StrategyHealthStatus.HEALTHY: 0,
            StrategyHealthStatus.DEGRADED: 0,
            StrategyHealthStatus.DYING: 0,
            StrategyHealthStatus.DEAD: 0,
        }

        dead = []
        dying = []

        worst_status = StrategyHealthStatus.HEALTHY
        worst_priority = -1

        for report in self.reports:
            counts[report.status] += 1

            priority = _STATUS_PRIORITY[report.status]
            if priority > worst_priority:
                worst_priority = priority
                worst_status = report.status

            if report.status == StrategyHealthStatus.DEAD:
                dead.append(report.strategy_id)
            elif report.status == StrategyHealthStatus.DYING:
                dying.append(report.strategy_id)

        # ----------------------------
        # GOVERNANCE PRESSURE SIGNALS
        # ----------------------------

        # Promotion: upside exists
        promotion_pressure = (
            counts[StrategyHealthStatus.HEALTHY] >= max(1, total // 2)
            and counts[StrategyHealthStatus.DEAD] == 0
        )

        # Demotion: downside risk exists
        demotion_pressure = (
            counts[StrategyHealthStatus.DEGRADED] > 0
            or counts[StrategyHealthStatus.DYING] > 0
            or counts[StrategyHealthStatus.DEAD] > 0
        )

        object.__setattr__(self, "total_strategies", total)
        object.__setattr__(self, "status_counts", counts)
        object.__setattr__(self, "overall_status", worst_status)
        object.__setattr__(self, "dead_strategies", dead)
        object.__setattr__(self, "dying_strategies", dying)
        object.__setattr__(self, "promotion_pressure", promotion_pressure)
        object.__setattr__(self, "demotion_pressure", demotion_pressure)
