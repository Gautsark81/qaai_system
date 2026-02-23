from abc import ABC, abstractmethod

from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot


class ExecutionTelemetrySnapshotProvider(ABC):
    """
    Optional extension for providers that expose invariant-aware telemetry.
    """

    @abstractmethod
    def get_telemetry_snapshot(self) -> ExecutionTelemetrySnapshot:
        """
        Return execution telemetry + invariant results.

        Must be read-only.
        """
        raise NotImplementedError
