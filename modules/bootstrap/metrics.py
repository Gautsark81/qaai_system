# modules/bootstrap/metrics.py

from modules.metrics.registry import MetricsRegistry
from modules.metrics.sink import MetricsSink
from modules.metrics.sinks.console import ConsoleMetricsSink
from modules.metrics.sinks.composite import CompositeMetricsSink
from modules.runtime.context import get_runtime_flags


def build_metrics_registry() -> MetricsRegistry:
    flags = get_runtime_flags()

    if not flags.METRICS_ENABLED:
        return MetricsRegistry(MetricsSink())

    sinks = [ConsoleMetricsSink()]
    return MetricsRegistry(CompositeMetricsSink(sinks))
