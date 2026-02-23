from optimization.latency_metrics import LatencyMetrics
from optimization.cost_metrics import CostMetrics


def efficiency_report(
    latency: LatencyMetrics,
    cost: CostMetrics,
) -> dict:

    return {
        "latency_ok": latency.order_to_ack_ms < 500,
        "slippage_ok": cost.slippage_cost < cost.brokerage_paid,
    }
