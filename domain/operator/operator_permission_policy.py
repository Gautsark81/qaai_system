class OperatorPermissionPolicy:
    """
    Defines what actions operators may take.
    """

    ALLOWED_ACTIONS = {
        "VIEW",
        "APPROVE",
        "PAUSE",
        "KILL",
    }

    @staticmethod
    def allow(action: str) -> bool:
        return action in OperatorPermissionPolicy.ALLOWED_ACTIONS
