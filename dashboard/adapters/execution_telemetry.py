from dashboard.view_models import (
    ExecutionTelemetryVM,
    ExecutionEventVM,
    ExecutionInvariantVM,
)
from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot


def execution_telemetry_adapter(
    snapshot: ExecutionTelemetrySnapshot,
) -> ExecutionTelemetryVM:
    telemetry = snapshot.telemetry
    invariants = snapshot.invariants

    return ExecutionTelemetryVM(
        execution_id=telemetry.execution_id,
        started_at=telemetry.started_at,
        completed_at=telemetry.completed_at,
        total_orders=telemetry.total_orders,
        filled_orders=telemetry.filled_orders,
        rejected_orders=telemetry.rejected_orders,
        cancelled_orders=telemetry.cancelled_orders,
        events=tuple(
            ExecutionEventVM(
                timestamp=e.timestamp,
                event_type=e.event_type,
                message=e.message,
            )
            for e in telemetry.events
        ),
        invariant_violations=tuple(
            ExecutionInvariantVM(
                code=v.code,
                message=v.message,
                detected_at=v.detected_at,
            )
            for v in invariants.violations
        ),
    )
