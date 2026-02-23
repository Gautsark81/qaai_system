# modules/operator_dashboard/tests/test_system_health.py

from operator_dashboard.state_assembler import DashboardStateAssembler

def test_system_health_has_required_fields():
    sys = DashboardStateAssembler().assemble().system

    for field in [
        "trading_mode",
        "kill_switch",
        "broker_connected",
        "capital_utilization_pct",
        "system_status",
    ]:
        assert hasattr(sys, field)
