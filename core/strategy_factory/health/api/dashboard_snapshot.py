from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from core.strategy_factory.health.dashboard.dashboard_view_models import (
    StrategyRowVM,
    PortfolioSummaryVM,
    NotificationFeedItemVM,
)


@dataclass(frozen=True)
class DashboardSnapshot:
    """
    Read-only, serializable dashboard snapshot.

    Pure export object:
    - No logic
    - No IO
    - No mutation
    """

    portfolio_summary: PortfolioSummaryVM
    strategy_rows: List[StrategyRowVM]
    notifications: List[NotificationFeedItemVM]
    as_of: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "as_of": self.as_of.isoformat(),
            "portfolio_summary": self._summary_to_dict(),
            "strategy_rows": [self._row_to_dict(r) for r in self.strategy_rows],
            "notifications": [
                self._notification_to_dict(n) for n in self.notifications
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    # ----------------------------
    # Internal serialization helpers
    # ----------------------------

    def _summary_to_dict(self) -> Dict[str, Any]:
        return {
            "total_strategies": self.portfolio_summary.total_strategies,
            "counts": {
                k.value: v
                for k, v in self.portfolio_summary.counts.items()
            },
            "overall_health": self.portfolio_summary.overall_health.value,
            "promotion_pressure": self.portfolio_summary.promotion_pressure,
            "demotion_pressure": self.portfolio_summary.demotion_pressure,
        }

    def _row_to_dict(self, row: StrategyRowVM) -> Dict[str, Any]:
        return {
            "strategy_id": row.strategy_id,
            "health_status": row.health_status.value,
            "lifecycle_action": row.lifecycle_action.value,
            "health_score": row.health_score,
            "reasons": list(row.reasons),
            "last_event_at": (
                row.last_event_at.isoformat()
                if row.last_event_at is not None
                else None
            ),
        }

    def _notification_to_dict(
        self, n: NotificationFeedItemVM
    ) -> Dict[str, Any]:
        return {
            "strategy_id": n.strategy_id,
            "action": n.action.value,
            "message": n.message,
            "timestamp": n.timestamp.isoformat(),
        }
