from abc import ABC, abstractmethod
from .event import TelemetryEvent


class TelemetrySink(ABC):

    @abstractmethod
    def emit(self, event: TelemetryEvent) -> None:
        """Persist or forward a telemetry event."""
        raise NotImplementedError
