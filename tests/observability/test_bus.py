from qaai_system.observability import EventBus, EventSink


class DummySink(EventSink):
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


def test_event_bus_fanout():
    sink1 = DummySink()
    sink2 = DummySink()

    bus = EventBus([sink1, sink2])

    bus.publish("event")

    assert sink1.events == ["event"]
    assert sink2.events == ["event"]
