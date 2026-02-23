from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class ReplayDiffItem:
    """
    Single detected difference between live and replayed execution.
    """
    code: str
    message: str


@dataclass(frozen=True)
class ReplayDiffReport:
    """
    Full diff report for a replay vs live comparison.
    """
    execution_id: str
    replay_id: str
    compared_at: datetime
    diffs: Tuple[ReplayDiffItem, ...]
