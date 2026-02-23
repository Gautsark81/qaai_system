import json
from pathlib import Path
from ..event import TelemetryEvent
from ..sink import TelemetrySink


class JsonlSink(TelemetrySink):

    def __init__(self, path: Path):
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: TelemetryEvent) -> None:
        with self._path.open("a", encoding="utf-8") as f:
            json.dump(event.__dict__, f, default=str)
            f.write("\n")
