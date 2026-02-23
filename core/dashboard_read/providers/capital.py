# core/dashboard_read/providers/capital.py

from core.dashboard_read.snapshot import CapitalState
from core.dashboard_read.providers._sources import capital as capital_source


def build_capital_state() -> CapitalState:
    m = capital_source.read_capital_metrics()

    return CapitalState(
        total_capital=m.total_capital,
        allocated_capital=m.allocated_capital,
        free_capital=m.free_capital,
        utilization_ratio=m.utilization_ratio,
        throttle_active=m.throttle_active,
    )