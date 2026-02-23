from abc import ABC, abstractmethod
from core.execution.telemetry import ExecutionTelemetry


class ExecutionTelemetryProvider(ABC):
    """
    Interface for execution telemetry sources.
    """

    @abstractmethod
    def get_telemetry(self) -> ExecutionTelemetry:
        """
        Return current execution telemetry snapshot.
        Must never mutate execution state.
        """
        raise NotImplementedError
