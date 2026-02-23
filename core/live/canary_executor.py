from core.live.canary_contracts import CanaryDeployment
from core.live.canary_guards import CanaryLimits
from core.safety.kill_switch import KillSwitch


class CanaryExecutor:
    """
    Live canary wrapper. Does NOT scale. Does NOT override.
    """

    def __init__(self, limits: CanaryLimits):
        self.limits = limits
        self.kill_switch = KillSwitch(scope="canary")

    def start(self, deployment: CanaryDeployment) -> None:
        # Arm kill switch immediately
        self.kill_switch.arm()

        # Canary execution hook (delegates to existing live executor)
        # NOTE: execution engine already exists in core/live/
        # This wrapper only enforces guardrails.
        pass
