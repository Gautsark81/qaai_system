from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict

from operator_dashboard.alerts.alert_types import AlertType


@dataclass(frozen=True)
class AlertEvent:
    alert_type: AlertType
    strategy_id: Optional[str]
    message: str
    severity: str          # info | warning | critical
    metadata: Dict[str, str]
    occurred_at: datetime

    @staticmethod
    def now(
        *,
        alert_type: AlertType,
        message: str,
        severity: str,
        strategy_id: Optional[str] = None,
        metadata: Dict[str, str] | None = None,
    ) -> "AlertEvent":
        return AlertEvent(
            alert_type=alert_type,
            strategy_id=strategy_id,
            message=message,
            severity=severity,
            metadata=metadata or {},
            occurred_at=datetime.now(timezone.utc),
        )
