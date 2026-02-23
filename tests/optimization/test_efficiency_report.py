from optimization.latency_metrics import LatencyMetrics
from optimization.cost_metrics import CostMetrics
from optimization.efficiency_report import efficiency_report


def test_efficiency_report():
    r = efficiency_report(
        LatencyMetrics(200, 50),
        CostMetrics(100, 20),
    )
    assert r["latency_ok"] is True
