from pathlib import Path
from typing import Iterable

from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot
from core.execution.telemetry_store import ExecutionTelemetryStore
from core.execution.telemetry_serializer import (
    serialize_snapshot,
    deserialize_snapshot,
)


class FileSystemTelemetryStore(ExecutionTelemetryStore):
    """
    Append-only filesystem-backed telemetry store.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _file_for(self, execution_id: str) -> Path:
        return self.base_dir / f"{execution_id}.jsonl"

    def append(self, snapshot: ExecutionTelemetrySnapshot) -> None:
        path = self._file_for(snapshot.telemetry.execution_id)
        line = serialize_snapshot(snapshot)

        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def get_by_execution_id(
        self, execution_id: str
    ) -> Iterable[dict]:
        path = self._file_for(execution_id)

        if not path.exists():
            return []

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                yield deserialize_snapshot(line)
