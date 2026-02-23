# modules/operator_dashboard/tests/test_strategy_pages.py

from operator_dashboard.state_assembler import DashboardStateAssembler

def test_strategies_have_required_fields():
    state = DashboardStateAssembler().assemble()

    for s in state.strategies:
        assert s.strategy_id
        assert s.lifecycle_stage
        assert s.status

def test_allowed_strategies_are_not_blocked():
    state = DashboardStateAssembler().assemble()

    for s in state.strategies:
        if s.status == "allowed":
            assert not s.kill_switch_active
