# tests/metrics/test_metrics_registry.py

from modules.metrics.registry import MetricsRegistry
from modules.metrics.sink import MetricsSink


class CapturingSink(MetricsSink):
    def __init__(self):
        self.samples = []

    def _emit(self, sample):
        self.samples.append(sample)


def test_counter_emits_sample():
    sink = CapturingSink()
    reg = MetricsRegistry(sink)

    reg.counter("test.counter", 1, {"a": "b"})

    assert len(sink.samples) == 1
    s = sink.samples[0]
    assert s.name == "test.counter"
    assert s.value == 1
    assert s.labels["a"] == "b"


def test_timer_emits_latency():
    sink = CapturingSink()
    reg = MetricsRegistry(sink)

    with reg.timer("test.timer"):
        pass

    assert len(sink.samples) == 1
    assert sink.samples[0].value >= 0.0
