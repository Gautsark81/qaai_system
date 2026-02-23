from datetime import datetime
from typing import Iterable, Tuple

from core.execution.telemetry import ExecutionTelemetry
from core.execution.invariants import (
    InvariantResult,
    InvariantViolation,
)
from core.execution.invariant_rules import (
    counts_do_not_exceed_total,
    completion_time_consistency,
    events_are_time_ordered,
)


INVARIANT_RULES = (
    counts_do_not_exceed_total,
    completion_time_consistency,
    events_are_time_ordered,
)


def validate_execution_invariants(
    telemetry: ExecutionTelemetry,
    rules: Iterable = INVARIANT_RULES,
) -> InvariantResult:
    """
    Validate execution telemetry against invariant rules.

    Never raises.
    Never mutates telemetry.
    """
    violations: list[InvariantViolation] = []

    for rule in rules:
        try:
            violation = rule(telemetry)
        except Exception:
            # Invariant engine must never crash the system
            violation = InvariantViolation(
                code="INVARIANT_EVALUATION_ERROR",
                message=f"Invariant {rule.__name__} raised unexpectedly",
                detected_at=datetime.utcnow(),
            )

        if violation is not None:
            violations.append(violation)

    return InvariantResult(
        execution_id=telemetry.execution_id,
        checked_at=datetime.utcnow(),
        violations=tuple(violations),
    )
