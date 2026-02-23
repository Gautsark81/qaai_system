from ..event import TelemetryEvent
from ..sink import TelemetrySink


class NullSink(TelemetrySink):
    def emit(self, event: TelemetryEvent) -> None:
        return
