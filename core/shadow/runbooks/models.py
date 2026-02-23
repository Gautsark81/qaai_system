from enum import Enum


class RunbookEvent(str, Enum):
    """
    Canonical runbook events.
    """
    FORCED_SHUTDOWN = "FORCED_SHUTDOWN"
    GRACEFUL_HALT = "GRACEFUL_HALT"
    RECOVERY_REPLAY = "RECOVERY_REPLAY"
