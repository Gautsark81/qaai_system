class LifecycleAlphaAdapter:
    """
    Lifecycle gate for alpha usage.

    🚨 v2 NEVER mutates lifecycle.
    This adapter only answers: ALLOW or BLOCK.
    """

    BLOCKED_STATES = {
        "DEGRADED",
        "SUSPENDED",
        "RETIRED",
    }

    def allow_alpha(self, lifecycle_state: str) -> str:
        if lifecycle_state in self.BLOCKED_STATES:
            return "BLOCK"
        return "ALLOW"
