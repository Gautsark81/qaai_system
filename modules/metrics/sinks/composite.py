# modules/metrics/sinks/composite.py

from typing import Iterable

from modules.metrics.sink import MetricsSink
from modules.metrics.types import MetricSample


class CompositeMetricsSink(MetricsSink):
    def __init__(self, sinks: Iterable[MetricsSink]):
        self._sinks = list(sinks)

    def _emit(self, sample: MetricSample) -> None:
        for sink in self._sinks:
            try:
                sink.emit(sample)
            except Exception:
                continue
