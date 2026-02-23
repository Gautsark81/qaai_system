from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class CooldownTracker:
    started_at: datetime
    duration_days: int

    def is_expired(self, now: datetime) -> bool:
        return now >= self.started_at + timedelta(days=self.duration_days)
