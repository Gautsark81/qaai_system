from typing import List
from .sink import EventSink


class EventBus:
    """
    Fan-out bus for observability events.
    """

    def __init__(self, sinks: List[EventSink]):
        self._sinks = list(sinks)

    def publish(self, event):
        for sink in self._sinks:
            sink.emit(event)
