# modules/operator_dashboard/tests/test_system_overview.py

from operator_dashboard.state_assembler import DashboardStateAssembler

def test_system_health_fields_exist():
    state = DashboardStateAssembler().assemble()
    sys = state.system

    for field in [
        "trading_mode",
        "kill_switch",
        "broker_connected",
        "system_status",
        "capital_utilization_pct",
    ]:
        assert hasattr(sys, field)

def test_kill_switch_forces_red():
    state = DashboardStateAssembler().assemble()
    sys = state.system

    if sys.kill_switch:
        assert sys.system_status == "RED"
