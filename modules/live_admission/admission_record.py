from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class LiveAdmissionRecord:
    strategy_id: str
    capital: float
    admitted_at: datetime
    expires_at: datetime
    token_session_id: str
    revoked_at: Optional[datetime] = None

    def is_active(self, now: datetime) -> bool:
        if self.revoked_at:
            return False
        return self.admitted_at <= now <= self.expires_at
