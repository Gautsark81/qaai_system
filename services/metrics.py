"""
Simple Prometheus pushgateway helper (optional).
"""
import os
import logging
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

logger = logging.getLogger("metrics")

def start_prometheus_push():
    gateway = os.getenv("PROMETHEUS_PUSHGATEWAY")
    if not gateway:
        return None
    registry = CollectorRegistry()
    gauge = Gauge("live_market_up", "1 if live_market is up", registry=registry)
    gauge.set(1)
    try:
        push_to_gateway(gateway, job='live_market', registry=registry)
    except Exception:
        logger.exception("prometheus push failed")
    # Return a simple object with close method to allow future extension
    class Dummy:
        def close(self):
            try:
                gauge.set(0)
                push_to_gateway(gateway, job='live_market', registry=registry)
            except Exception:
                pass
    return Dummy()
