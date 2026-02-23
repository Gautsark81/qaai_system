from datetime import datetime
from typing import Tuple

from core.execution.telemetry import ExecutionEvent, ExecutionTelemetry


def build_shadow_telemetry(
    execution_id: str,
    events: Tuple[ExecutionEvent, ...],
    *,
    total_orders: int,
    filled_orders: int,
    rejected_orders: int,
    cancelled_orders: int,
) -> ExecutionTelemetry:
    """
    Build execution telemetry for shadow executions.
    """
    started_at = events[0].timestamp if events else datetime.utcnow()
    completed_at = events[-1].timestamp if events else started_at

    return ExecutionTelemetry(
        execution_id=execution_id,
        started_at=started_at,
        completed_at=completed_at,
        total_orders=total_orders,
        filled_orders=filled_orders,
        rejected_orders=rejected_orders,
        cancelled_orders=cancelled_orders,
        events=events,
    )
