# core/tournament/tournament_metrics.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional


# ============================================================
# StrategyMetrics — Immutable Phase T-3 Artifact
# ============================================================

@dataclass(frozen=True)
class StrategyMetrics:
    """
    Phase T-3 metrics artifact.

    IMPORTANT INVARIANTS:
    - Immutable (frozen)
    - Deterministic
    - No thresholds
    - No promotion or ranking logic
    - SSR is a RATIO (0.0–1.0), NOT percentage
    """

    # --- Identity & Versioning ---
    strategy_id: str
    metrics_version: str
    computed_at: datetime

    # --- Core Counts ---
    total_trades: int
    winning_trades: int
    losing_trades: int

    # --- Canonical Metric ---
    ssr: float  # Strategy Success Ratio (0.0 – 1.0)

    # --- Risk & Stability ---
    max_drawdown_pct: float
    max_single_loss_pct: float

    # --- Quality ---
    avg_rr: float
    expectancy: float

    # --- Exposure ---
    time_in_market_pct: float
    avg_trade_duration: float

    # --- Sensitivity ---
    volatility_sensitivity: Dict[str, float]

    # --- Meta ---
    symbol_count: int
    notes: List[str] = field(default_factory=list)


# ============================================================
# Metric Computation Helpers (PURE FUNCTIONS)
# ============================================================

def compute_ssr(wins: int, total: int) -> float:
    if total == 0:
        return 0.0
    return wins / total


def compute_max_drawdown(equity_curve: List[float]) -> float:
    if not equity_curve:
        return 0.0

    peak = equity_curve[0]
    max_dd = 0.0

    for value in equity_curve:
        peak = max(peak, value)
        drawdown = (peak - value) / peak if peak != 0 else 0.0
        max_dd = max(max_dd, drawdown)

    return max_dd * 100.0  # percentage


def compute_expectancy(
    wins: int,
    losses: int,
    avg_win: float,
    avg_loss: float,
) -> float:
    total = wins + losses
    if total == 0:
        return 0.0

    win_rate = wins / total
    loss_rate = losses / total
    return (win_rate * avg_win) - (loss_rate * abs(avg_loss))


# ============================================================
# StrategyMetrics Builder
# ============================================================

def build_strategy_metrics(
    *,
    strategy_id: str,
    trades: Iterable,
    equity_curve: List[float],
    symbol_count: int,
    avg_trade_duration: float,
    time_in_market_pct: float,
    avg_win: float,
    avg_loss: float,
    avg_rr: float,
    max_single_loss_pct: float,
    volatility_sensitivity: Optional[Dict[str, float]] = None,
    metrics_version: str = "v1",
) -> StrategyMetrics:
    """
    Build a StrategyMetrics artifact from raw tournament results.

    This function is:
    - Pure
    - Deterministic
    - Side-effect free
    """

    trades = list(trades)
    total_trades = len(trades)

    winning_trades = sum(1 for t in trades if t.pnl > 0)
    losing_trades = sum(1 for t in trades if t.pnl <= 0)

    ssr = compute_ssr(winning_trades, total_trades)
    max_dd = compute_max_drawdown(equity_curve)
    expectancy = compute_expectancy(
        winning_trades,
        losing_trades,
        avg_win,
        avg_loss,
    )

    return StrategyMetrics(
        strategy_id=strategy_id,
        metrics_version=metrics_version,
        computed_at=datetime.now(timezone.utc),

        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,

        ssr=ssr,

        max_drawdown_pct=max_dd,
        max_single_loss_pct=max_single_loss_pct,

        avg_rr=avg_rr,
        expectancy=expectancy,

        time_in_market_pct=time_in_market_pct,
        avg_trade_duration=avg_trade_duration,

        volatility_sensitivity=volatility_sensitivity or {},

        symbol_count=symbol_count,
        notes=[],
    )
