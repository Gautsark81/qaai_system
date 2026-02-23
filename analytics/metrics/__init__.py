"""
Metrics subpackage.

Exposes metric recorders that are safe to use in:
- live trading loops
- backtest and simulation runs
- async or sync contexts

Design goals:
- No hard external dependencies
- Fail-closed: metrics must never break trading
- Easy to swap/extend sinks (file, TSDB, Prometheus etc.)
"""

from .base import MetricsSink, LoggingMetricsSink, MetricContext
from .cycle_metrics import (
    CycleMetricsRecorder,
    record_cycle_metrics,
    DEFAULT_METRICS_PATH,
)

__all__ = [
    "MetricsSink",
    "LoggingMetricsSink",
    "MetricContext",
    "CycleMetricsRecorder",
    "record_cycle_metrics",
    "DEFAULT_METRICS_PATH",
]
