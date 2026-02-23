from dataclasses import dataclass
from core.execution.mode import ExecutionMode


@dataclass(frozen=True)
class ExecutionContext:
    """
    Immutable execution context.
    """
    mode: ExecutionMode
    broker_name: str
