from domain.canary.canary_mode import CanaryMode


class CanaryExecutionRouter:
    """
    Routes execution based on canary mode.
    """

    @staticmethod
    def route(mode: CanaryMode) -> str:
        if mode == CanaryMode.LIVE:
            return "LIVE_EXECUTION"
        if mode == CanaryMode.PAPER:
            return "PAPER_EXECUTION"
        return "NO_EXECUTION"
