from typing import Iterable, List
from .event import TelemetryEvent
from .sink import TelemetrySink


class TelemetryEmitter:
    """
    Central emission point.
    No global state.
    """

    def __init__(self, sinks: Iterable[TelemetrySink]):
        self._sinks: List[TelemetrySink] = list(sinks)
        if not self._sinks:
            raise ValueError("At least one telemetry sink is required")

    def emit(self, event: TelemetryEvent) -> None:
        for sink in self._sinks:
            sink.emit(event)
