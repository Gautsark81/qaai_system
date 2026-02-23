# modules/metrics/sink.py

from modules.metrics.types import MetricSample


class MetricsSink:
    """
    Base metrics sink.

    HARD GUARANTEES:
    - Must never raise
    - Must never block core logic
    """

    def emit(self, sample: MetricSample) -> None:
        try:
            self._emit(sample)
        except Exception:
            return

    def _emit(self, sample: MetricSample) -> None:
        # Default no-op
        return
