# modules/observability/execution_metrics.py
import threading
from datetime import datetime
from typing import Optional
from .models import BrokerExecutionMetric


class ExecutionMetricsSink:
    """
    Non-blocking, best-effort execution metrics recorder.
    NEVER raises.
    """

    def __init__(self, writer):
        self._writer = writer

    def record(
        self,
        *,
        broker: str,
        event: str,
        order_id: str,
        symbol: str,
        latency_ms: Optional[float] = None,
    ) -> None:
        metric = BrokerExecutionMetric(
            timestamp=datetime.utcnow(),
            broker=broker,
            event=event,
            latency_ms=latency_ms,
            order_id=order_id,
            symbol=symbol,
        )

        # fire-and-forget
        threading.Thread(
            target=self._safe_write,
            args=(metric,),
            daemon=True,
        ).start()

    def _safe_write(self, metric: BrokerExecutionMetric) -> None:
        try:
            self._writer.write(metric)
        except Exception:
            # NEVER propagate
            pass
