from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot
from core.execution.telemetry_store import ExecutionTelemetryStore


def persist_telemetry_snapshot(
    snapshot: ExecutionTelemetrySnapshot,
    store: ExecutionTelemetryStore,
) -> None:
    """
    Persist execution telemetry snapshot.

    Must never raise into execution or UI paths.
    """
    try:
        store.append(snapshot)
    except Exception:
        # Persistence must never affect execution
        pass
