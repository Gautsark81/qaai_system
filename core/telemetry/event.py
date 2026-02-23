from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from .types import TelemetryCategory, TelemetrySeverity


@dataclass(frozen=True)
class TelemetryEvent:
    event_id: str
    category: TelemetryCategory
    severity: TelemetrySeverity
    timestamp: datetime

    run_id: str
    strategy_id: Optional[str]
    order_id: Optional[str]
    parent_event_id: Optional[str]

    payload: Dict[str, Any]

    @staticmethod
    def create(
        *,
        category: TelemetryCategory,
        severity: TelemetrySeverity,
        run_id: str,
        payload: Dict[str, Any],
        strategy_id: Optional[str] = None,
        order_id: Optional[str] = None,
        parent_event_id: Optional[str] = None,
    ) -> "TelemetryEvent":
        if not run_id:
            raise ValueError("run_id is mandatory for telemetry")

        return TelemetryEvent(
            event_id=str(uuid4()),
            category=category,
            severity=severity,
            timestamp=datetime.now(timezone.utc),
            run_id=run_id,
            strategy_id=strategy_id,
            order_id=order_id,
            parent_event_id=parent_event_id,
            payload=dict(payload),  # defensive copy
        )
