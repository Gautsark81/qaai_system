from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from core.strategy_factory.health.strategy_health_report import (
    StrategyHealthReport,
    StrategyHealthStatus,
)
from core.strategy_factory.health.lifecycle.strategy_lifecycle_controller import (
    StrategyLifecycleAction,
)
from core.strategy_factory.health.reports.strategy_health_aggregator import (
    StrategyHealthAggregator,
)
from core.strategy_factory.health.notifications.notifications_router import (
    Notification,
)


# ----------------------------
# Strategy Row
# ----------------------------

@dataclass(frozen=True)
class StrategyRowVM:
    """
    Read-only, presentation-friendly strategy row.
    """

    strategy_id: str
    health_status: StrategyHealthStatus
    lifecycle_action: StrategyLifecycleAction
    health_score: int
    reasons: List[str]
    last_event_at: Optional[datetime]

    @classmethod
    def from_domain(
        cls,
        *,
        report: StrategyHealthReport,
        lifecycle_action: StrategyLifecycleAction,
        last_event_at: Optional[datetime],
    ) -> "StrategyRowVM":
        return cls(
            strategy_id=report.strategy_id,
            health_status=report.status,
            lifecycle_action=lifecycle_action,
            health_score=report.health_score,
            reasons=list(report.reasons),
            last_event_at=last_event_at,
        )


# ----------------------------
# Portfolio Summary
# ----------------------------

@dataclass(frozen=True)
class PortfolioSummaryVM:
    """
    Read-only portfolio-level summary.
    """

    total_strategies: int
    counts: Dict[StrategyHealthStatus, int]
    overall_health: StrategyHealthStatus
    promotion_pressure: bool
    demotion_pressure: bool

    @classmethod
    def from_aggregator(
        cls, agg: StrategyHealthAggregator
    ) -> "PortfolioSummaryVM":
        return cls(
            total_strategies=agg.total_strategies,
            counts=dict(agg.status_counts),
            overall_health=agg.overall_status,
            promotion_pressure=agg.promotion_pressure,
            demotion_pressure=agg.demotion_pressure,
        )


# ----------------------------
# Notification Feed
# ----------------------------

@dataclass(frozen=True)
class NotificationFeedItemVM:
    """
    Read-only notification feed item.
    """

    strategy_id: str
    action: StrategyLifecycleAction
    message: str
    timestamp: datetime

    @classmethod
    def from_notification(
        cls, notification: Notification
    ) -> "NotificationFeedItemVM":
        return cls(
            strategy_id=notification.strategy_id,
            action=notification.action,
            message=notification.message,
            timestamp=notification.timestamp,
        )
