from modules.operator_dashboard.state_assembler import DashboardStateAssembler


def test_governance_visibility_contract():
    state = DashboardStateAssembler.assemble()

    for s in state.strategies:
        if s.approval is not None:
            assert s.approval.stage in {"paper", "live"}
            assert s.approval.status in {"approved", "rejected", "pending"}
            assert s.approval.reviewer is not None
