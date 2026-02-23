from pathlib import Path
from typing import Optional

from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot
from core.execution.telemetry_serializer import deserialize_snapshot


def load_latest_execution_telemetry(
    base_dir: Path,
) -> Optional[dict]:
    """
    Load the most recent execution telemetry snapshot from disk.
    Returns raw dict (rehydration happens later).
    """
    if not base_dir.exists():
        return None

    files = sorted(base_dir.glob("*.jsonl"))
    if not files:
        return None

    latest_file = files[-1]

    with latest_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            return None
        return deserialize_snapshot(lines[-1])
