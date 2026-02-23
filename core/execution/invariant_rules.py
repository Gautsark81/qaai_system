from datetime import datetime
from typing import Optional

from core.execution.telemetry import ExecutionTelemetry
from core.execution.invariants import InvariantViolation


def counts_do_not_exceed_total(
    telemetry: ExecutionTelemetry,
) -> Optional[InvariantViolation]:
    """
    filled + rejected + cancelled <= total_orders
    """
    total_outcomes = (
        telemetry.filled_orders
        + telemetry.rejected_orders
        + telemetry.cancelled_orders
    )

    if total_outcomes > telemetry.total_orders:
        return InvariantViolation(
            code="ORDER_COUNT_EXCEEDED",
            message=(
                "Sum of filled/rejected/cancelled orders "
                "exceeds total_orders"
            ),
            detected_at=datetime.utcnow(),
        )

    return None


def completion_time_consistency(
    telemetry: ExecutionTelemetry,
) -> Optional[InvariantViolation]:
    """
    completed_at must be >= started_at if present
    """
    if telemetry.completed_at is None:
        return None

    if telemetry.completed_at < telemetry.started_at:
        return InvariantViolation(
            code="COMPLETION_TIME_INVALID",
            message="completed_at precedes started_at",
            detected_at=datetime.utcnow(),
        )

    return None


def events_are_time_ordered(
    telemetry: ExecutionTelemetry,
) -> Optional[InvariantViolation]:
    """
    Events must be monotonically non-decreasing by timestamp
    """
    events = telemetry.events

    for i in range(1, len(events)):
        if events[i].timestamp < events[i - 1].timestamp:
            return InvariantViolation(
                code="EVENT_TIME_ORDER_VIOLATION",
                message="Execution events are not time-ordered",
                detected_at=datetime.utcnow(),
            )

    return None
