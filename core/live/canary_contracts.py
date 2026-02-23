from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List


@dataclass(frozen=True)
class CanaryDeployment:
    run_id: str
    strategy_id: str
    symbol_scope: List[str]
    capital_pct: float  # e.g. 0.25%
    started_at: datetime
    notes: List[str]

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
