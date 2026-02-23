from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CanaryHealth:
    strategy_id: str
    pnl_pct: float
    drawdown_pct: float
    latency_ms: float
    risk_blocks: int
    observed_at: datetime

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
