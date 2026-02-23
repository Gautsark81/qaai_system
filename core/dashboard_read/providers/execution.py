# core/dashboard_read/providers/execution.py

from core.dashboard_read.snapshot import (
    ExecutionState,
    ExecutionPosition,
)
from core.dashboard_read.providers._sources import execution as execution_source


def build_execution_state() -> ExecutionState:
    m = execution_source.read_execution_metrics()

    positions = [
        ExecutionPosition(
            symbol=p.symbol,
            quantity=p.quantity,
            exposure=p.exposure,
            stop_loss=p.stop_loss,
        )
        for p in m.positions
    ]

    return ExecutionState(
        intents_created=m.intents_created,
        intents_blocked=m.intents_blocked,
        blocked_reasons=m.blocked_reasons,
        positions=positions,
        fills=m.fills,
    )