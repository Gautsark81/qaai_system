# modules/operator_dashboard/tests/test_state_assembler.py

from operator_dashboard.state_assembler import DashboardStateAssembler

def test_dashboard_state_assembles():
    state = DashboardStateAssembler().assemble()

    assert state.system is not None
    assert isinstance(state.strategies, list)
    assert isinstance(state.alerts, list)
    assert state.timestamp is not None
