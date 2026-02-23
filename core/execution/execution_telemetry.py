from __future__ import annotations

from dataclasses import dataclass

from core.execution.execution_intent import ExecutionIntent


@dataclass(frozen=True)
class ExecutionTelemetry:
    """
    Immutable execution telemetry record.

    Properties:
    - Read-only
    - Deterministic
    - No persistence
    """

    mode: str
    symbol: str
    side: str
    quantity: int
    strategy_id: str
    intent: ExecutionIntent
