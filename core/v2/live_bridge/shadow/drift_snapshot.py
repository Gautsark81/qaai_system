from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DriftSnapshot:
    strategy_id: str
    paper_pnl: float
    live_pnl: float
    paper_trades: int
    live_trades: int
    captured_at: datetime
