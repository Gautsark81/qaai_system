from dataclasses import dataclass

from core.execution.telemetry import ExecutionTelemetry
from core.execution.invariants import InvariantResult


@dataclass(frozen=True)
class ExecutionTelemetrySnapshot:
    """
    Composite, read-only execution observability snapshot.
    """
    telemetry: ExecutionTelemetry
    invariants: InvariantResult
