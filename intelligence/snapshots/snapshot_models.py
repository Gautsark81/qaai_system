from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Any


@dataclass(frozen=True)
class StrategyMetricsSnapshot:
    # ---------- Identity ----------
    snapshot_id: str
    strategy_id: str
    strategy_version: str

    # ---------- Time ----------
    created_at: datetime
    window_start: datetime
    window_end: datetime
    window_type: str              # ROLLING | FIXED | EXPANDING

    # ---------- Lifecycle ----------
    stage: str                    # BACKTEST | PAPER | LIVE

    # ---------- Performance ----------
    ssr: float
    total_trades: int
    successful_trades: int
    win_rate: float
    expectancy: float
    max_drawdown: float

    # ---------- Intelligence ----------
    symbol_metrics: Dict[str, Dict[str, Any]]
    regime_metrics: Dict[str, Dict[str, Any]]

    # ---------- Risk / Governance ----------
    risk_events: List[Any] = field(default_factory=list)
    governance_flags: List[Any] = field(default_factory=list)

    # ---------- Metadata ----------
    notes: str = ""
    schema_version: str = "v3"

    # --------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        d["window_start"] = self.window_start.isoformat()
        d["window_end"] = self.window_end.isoformat()
        return d
