from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ShadowLiveState:
    strategy_id: str
    started_at: datetime
    capital: float
    peak_pnl: float
    current_pnl: float
    killed_at: Optional[datetime] = None

    def is_active(self) -> bool:
        return self.killed_at is None
