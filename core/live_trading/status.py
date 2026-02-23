from enum import Enum


class ExecutionStatus(str, Enum):
    """
    Execution-level status for LIVE strategies.
    Separate from lifecycle state.
    """

    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
