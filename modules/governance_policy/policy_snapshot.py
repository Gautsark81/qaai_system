from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PolicySnapshot:
    captured_at: datetime
    ssr_threshold: float
    max_drawdown_pct: float
    approval_ttl_hours: int
    max_capital: float
