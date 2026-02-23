# tests/metrics/test_metrics_safety.py

from modules.metrics.registry import MetricsRegistry
from modules.metrics.sink import MetricsSink


class ExplodingSink(MetricsSink):
    def _emit(self, sample):
        raise RuntimeError("boom")


def test_metrics_never_raise():
    reg = MetricsRegistry(ExplodingSink())

    # Must not raise
    reg.counter("x")
    with reg.timer("y"):
        pass
