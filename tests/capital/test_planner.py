from qaai_system.capital.planner import CapitalAllocationPlanner


def test_planner(snapshot):
    planner = CapitalAllocationPlanner()
    plan = planner.build_plan(
        snapshots=[snapshot],
        allocatable_capital=100000,
        stage="LIVE",
        correlation_map={},
    )

    assert plan.allocations[0].allocated_capital > 0
