import pytest

from modules.operator_dashboard.state_assembler import DashboardStateAssembler


@pytest.fixture
def snapshot_factory():
    """
    Minimal snapshot factory for dashboard adapter tests.

    Accepts optional strategy_state keyword for compatibility.
    """
    def _factory(*, strategy_state=None):
        snapshot = DashboardStateAssembler.assemble()

        # Inject strategy_state only if provided
        if strategy_state is not None:
            object.__setattr__(snapshot, "strategy_state", strategy_state)

        return snapshot

    return _factory