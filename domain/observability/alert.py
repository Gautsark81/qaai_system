from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Alert:
    severity: str     # LOW / MEDIUM / HIGH / CRITICAL
    source: str
    message: str
    created_at: datetime
