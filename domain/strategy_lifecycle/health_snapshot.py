from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class StrategyHealthSnapshot:
    strategy_id: str
    observed_at: datetime
    ssr_current: float
    ssr_reference: float
    drawdown_pct: float
    trade_count: int
    anomaly_flag: bool
    notes: Optional[str] = None
