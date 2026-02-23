# tests/test_metrics_shim.py
from modules.observability.metrics import Metrics

def test_metrics_shim_runs():
    m = Metrics()
    m.inc_order()
    m.inc_order_error()
    m.set_latency(0.123)
    # prometheus optional: ensure method doesn't crash
    _ = m.prometheus_metrics()
