class ExecutionEntryGate:
    """
    Final execution entry guard.

    Enforces permission result without inspecting policy.
    """

    @staticmethod
    def ensure_allowed(result):
        if result.permission.allowed is not True:
            raise PermissionError("Execution blocked by gate chain")
