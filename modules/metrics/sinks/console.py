# modules/metrics/sinks/console.py

from modules.metrics.sink import MetricsSink
from modules.metrics.types import MetricSample


class ConsoleMetricsSink(MetricsSink):
    def _emit(self, sample: MetricSample) -> None:
        label_str = " ".join(f"{k}={v}" for k, v in sample.labels.items())
        print(f"[METRIC] {sample.name}={sample.value:.3f} {label_str}")
