# modules/metrics/registry.py

import threading
import time
from contextlib import contextmanager
from typing import Mapping

from modules.metrics.types import MetricSample
from modules.metrics.sink import MetricsSink


class MetricsRegistry:
    """
    Central metrics registry.
    Emits samples to configured sink.
    """

    def __init__(self, sink: MetricsSink):
        self._sink = sink
        self._lock = threading.Lock()

    def counter(self, name: str, value: float = 1.0, labels: Mapping[str, str] | None = None):
        labels = labels or {}
        self._sink.emit(MetricSample(name=name, value=value, labels=labels))

    def gauge(self, name: str, value: float, labels: Mapping[str, str] | None = None):
        labels = labels or {}
        self._sink.emit(MetricSample(name=name, value=value, labels=labels))

    @contextmanager
    def timer(self, name: str, labels: Mapping[str, str] | None = None):
        labels = labels or {}
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self._sink.emit(
                MetricSample(
                    name=name,
                    value=elapsed_ms,
                    labels=labels,
                )
            )
