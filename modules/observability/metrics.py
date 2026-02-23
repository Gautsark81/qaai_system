# modules/observability/metrics.py
from __future__ import annotations
import logging
from typing import Optional

_logger = logging.getLogger("qaai.metrics")

try:
    from prometheus_client import Counter, Gauge, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except Exception:
    PROMETHEUS_AVAILABLE = False

class Metrics:
    def __init__(self, namespace: str = "qaai"):
        self.namespace = namespace
        if PROMETHEUS_AVAILABLE:
            self._registry = CollectorRegistry()
            self.order_counter = Counter(f"{namespace}_orders_total", "Total orders", registry=self._registry)
            self.order_errors = Counter(f"{namespace}_order_errors_total", "Order errors", registry=self._registry)
            self.latency = Gauge(f"{namespace}_latency_seconds", "Latency seconds", registry=self._registry)
        else:
            self.order_counter = None
            self.order_errors = None
            self.latency = None

    def inc_order(self, n: int = 1):
        if PROMETHEUS_AVAILABLE:
            self.order_counter.inc(n)
        else:
            _logger.info("metric order_inc %s", n)

    def inc_order_error(self, n: int = 1):
        if PROMETHEUS_AVAILABLE:
            self.order_errors.inc(n)
        else:
            _logger.info("metric order_error %s", n)

    def set_latency(self, v: float):
        if PROMETHEUS_AVAILABLE:
            self.latency.set(v)
        else:
            _logger.debug("metric latency %s", v)

    def prometheus_metrics(self) -> Optional[bytes]:
        if PROMETHEUS_AVAILABLE:
            return generate_latest(self._registry)
        return None
