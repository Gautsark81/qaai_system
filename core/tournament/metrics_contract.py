# core/tournament/metrics_contract.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass(frozen=True)
class StrategyMetrics:
    """
    Phase T-3 Metrics Contract (IMMUTABLE)

    Invariants:
    - Read-only
    - Deterministic
    - No thresholds
    - No ranking
    - No promotion logic
    """

    # ---- Identity / Versioning ----
    strategy_id: str
    metrics_version: str
    computed_at: datetime

    # ---- Core Counts ----
    total_trades: int
    win_trades: int
    loss_trades: int

    # ---- Canonical Metric ----
    ssr: float  # Strategy Success Ratio (0.0 – 1.0)

    # ---- Risk ----
    max_drawdown_pct: float
    max_single_loss_pct: float

    # ---- Quality ----
    avg_rr: float
    expectancy: float

    # ---- Exposure ----
    time_in_market_pct: float
    avg_trade_duration: float

    # ---- Sensitivity ----
    volatility_sensitivity: Dict[str, float]

    # ---- Meta ----
    symbol_count: int
    notes: List[str] = field(default_factory=list)

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)
