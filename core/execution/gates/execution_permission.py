from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class ExecutionPermission:
    """
    Final execution admission artifact.

    This object:
    - Is immutable
    - Is replay-safe
    - Contains no policy logic
    """

    allowed: bool
    reasons: List[str] = field(default_factory=list)

    @staticmethod
    def allowed_permission(reasons: List[str]) -> "ExecutionPermission":
        return ExecutionPermission(
            allowed=True,
            reasons=list(reasons),
        )

    @staticmethod
    def denied_permission(reasons: List[str]) -> "ExecutionPermission":
        return ExecutionPermission(
            allowed=False,
            reasons=list(reasons),
        )
