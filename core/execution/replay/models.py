from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


class ReplayMode(Enum):
    """
    How the replay should be interpreted.
    """
    DRY_RUN = auto()       # Validate logic only
    FULL_REPLAY = auto()   # Reconstruct execution path


@dataclass(frozen=True)
class ReplayIdentity:
    """
    Stable identity for a replay request.
    """
    replay_id: str
    execution_id: str
    requested_at: datetime
    mode: ReplayMode
