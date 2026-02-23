from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OperatorAlert:
    """
    Human-facing alert.
    """
    timestamp: datetime
    level: str
    message: str
