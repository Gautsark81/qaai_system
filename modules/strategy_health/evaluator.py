# modules/strategy_health/evaluator.py

from dataclasses import dataclass
from typing import Dict, List, Optional
import statistics


# ==========================================================
# Utilities
# ==========================================================

def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def _max_drawdown_pct(equity: List[float]) -> float:
    """
    Returns max drawdown as a percentage (0.0 – 1.0)
    """
    if not equity or equity[0] <= 0:
        return 0.0

    peak = equity[0]
    max_dd = 0.0

    for v in equity:
        if v > peak:
            peak = v
        dd = (peak - v) / peak
        max_dd = max(max_dd, dd)

    return max_dd


# ==========================================================
# Result Contract
# ==========================================================

@dataclass(frozen=True)
class HealthResult:
    strategy_id: str
    health_score: float          # 0.0 – 1.0
    signals: Dict[str, float]    # normalized sub-scores
    flags: List[str]             # informational flags
    window: int
    reason: str


# ==========================================================
# Strategy Health Evaluator
# ==========================================================

class StrategyHealthEvaluator:
    """
    Deterministic, broker-agnostic strategy health evaluator.

    Drawdown doctrine (LOCKED):
      - 0–2%   : Ideal
      - 2–5%   : Acceptable
      - 5–8%   : Degraded
      - >8%    : CRITICAL
    """

    def __init__(
        self,
        *,
        min_trades: int = 20,
    ):
        self.min_trades = min_trades

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def evaluate(
        self,
        *,
        strategy_id: str,
        trade_pnls: List[float],
        equity_curve: List[float],
        timestamps: Optional[List[int]] = None,
        volatility_regime: Optional[str] = None,
        window: int = 50,
    ) -> HealthResult:

        flags: List[str] = []

        # -------------------------
        # Data sufficiency
        # -------------------------
        if len(trade_pnls) < self.min_trades:
            flags.append("INSUFFICIENT_TRADES")

        trades = trade_pnls[-window:]
        equity = equity_curve[-window:] if equity_curve else []

        # -------------------------
        # Win-rate (≥80% HARD TARGET)
        # -------------------------
        wins = sum(1 for p in trades if p > 0)
        total = max(1, len(trades))
        win_rate = wins / total

        if win_rate >= 0.80:
            win_rate_score = 1.0
        elif win_rate >= 0.70:
            win_rate_score = 0.6
        elif win_rate >= 0.60:
            win_rate_score = 0.4
        else:
            win_rate_score = 0.0
            flags.append("WIN_RATE_INVALID")

        if win_rate < 0.80:
            flags.append("WIN_RATE_BELOW_80")

        # -------------------------
        # Expectancy
        # -------------------------
        mean_pnl = statistics.mean(trades) if trades else 0.0
        max_abs = max((abs(p) for p in trades), default=1.0)
        expectancy_score = _clamp(mean_pnl / max_abs)

        if expectancy_score < 0.30:
            flags.append("EXPECTANCY_DECAY")

        # -------------------------
        # Drawdown (0–2% IDEAL)
        # -------------------------
        max_dd_pct = _max_drawdown_pct(equity)

        if max_dd_pct <= 0.02:
            drawdown_score = 1.0
        elif max_dd_pct <= 0.05:
            drawdown_score = 0.7
        elif max_dd_pct <= 0.08:
            drawdown_score = 0.4
            flags.append("DRAWDOWN_DEGRADED")
        else:
            drawdown_score = 0.0
            flags.append("DRAWDOWN_RISK")

        # -------------------------
        # Consistency
        # -------------------------
        variance = statistics.pvariance(trades) if len(trades) > 1 else 0.0
        consistency_score = _clamp(1.0 / (1.0 + variance))

        # -------------------------
        # Activity
        # -------------------------
        activity_score = _clamp(len(trades) / window)

        if activity_score < 0.30:
            flags.append("LOW_ACTIVITY")

        # -------------------------
        # Final health score (LOCKED WEIGHTS)
        # -------------------------
        health = (
            0.30 * drawdown_score
            + 0.25 * win_rate_score
            + 0.25 * expectancy_score
            + 0.10 * consistency_score
            + 0.10 * activity_score
        )

        signals = {
            "win_rate": round(win_rate_score, 4),
            "expectancy": round(expectancy_score, 4),
            "drawdown": round(drawdown_score, 4),
            "consistency": round(consistency_score, 4),
            "activity": round(activity_score, 4),
        }

        return HealthResult(
            strategy_id=strategy_id,
            health_score=round(_clamp(health), 4),
            signals=signals,
            flags=sorted(set(flags)),
            window=window,
            reason="Strategy health evaluated (drawdown 0–2% target)",
        )
