from pprint import pprint
from ..event import TelemetryEvent
from ..sink import TelemetrySink


class ConsoleSink(TelemetrySink):

    def emit(self, event: TelemetryEvent) -> None:
        pprint(event)
