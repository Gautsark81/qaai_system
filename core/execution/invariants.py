from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Callable

from core.execution.telemetry import ExecutionTelemetry


@dataclass(frozen=True)
class InvariantViolation:
    """
    Read-only record of an invariant violation.
    """
    code: str
    message: str
    detected_at: datetime


@dataclass(frozen=True)
class InvariantResult:
    """
    Result of running invariants against telemetry.
    """
    execution_id: str
    checked_at: datetime
    violations: Tuple[InvariantViolation, ...]
