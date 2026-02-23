from abc import ABC, abstractmethod
from typing import Iterable

from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot


class ExecutionTelemetryStore(ABC):
    """
    Append-only store for execution telemetry snapshots.
    """

    @abstractmethod
    def append(self, snapshot: ExecutionTelemetrySnapshot) -> None:
        """
        Persist a telemetry snapshot immutably.
        Must never mutate existing records.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_execution_id(
        self, execution_id: str
    ) -> Iterable[ExecutionTelemetrySnapshot]:
        """
        Return all snapshots for a given execution_id.
        """
        raise NotImplementedError
