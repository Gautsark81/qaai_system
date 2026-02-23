from core.execution.telemetry import ExecutionTelemetry
from core.execution.invariant_validator import (
    validate_execution_invariants,
)
from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot


def build_execution_telemetry_snapshot(
    telemetry: ExecutionTelemetry,
) -> ExecutionTelemetrySnapshot:
    """
    Build a composite execution telemetry snapshot.

    - Never mutates execution
    - Never raises
    """
    invariant_result = validate_execution_invariants(telemetry)

    return ExecutionTelemetrySnapshot(
        telemetry=telemetry,
        invariants=invariant_result,
    )
