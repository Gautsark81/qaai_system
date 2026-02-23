from domain.operator.operator_permission_policy import (
    OperatorPermissionPolicy
)


class OperatorCommandGate:
    """
    Final gate for operator actions.
    """

    @staticmethod
    def allow(action: str) -> bool:
        return OperatorPermissionPolicy.allow(action)
