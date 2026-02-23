# modules/operator_dashboard/tests/test_strategies.py

from operator_dashboard.state_assembler import DashboardStateAssembler

def test_strategies_are_well_formed():
    strategies = DashboardStateAssembler().assemble().strategies

    for s in strategies:
        assert s.strategy_id
        assert s.lifecycle_stage
        assert s.status
