from domain.canary.canary_execution_router import CanaryExecutionRouter
from domain.canary.canary_mode import CanaryMode


def test_canary_execution_routing():
    assert CanaryExecutionRouter.route(CanaryMode.LIVE) == "LIVE_EXECUTION"
    assert CanaryExecutionRouter.route(CanaryMode.OFF) == "NO_EXECUTION"
