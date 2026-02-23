from statistics import mean, pstdev

from core.strategy_health.contracts.dimension import HealthDimensionScore
from core.strategy_health.contracts.enums import DimensionVerdict


class PerformanceDimensionEvaluator:
    """
    Evaluates strategy performance health from realized returns.

    HARD INVARIANTS:
    - FAIL verdicts must have visibly poor scores
    - Flat != losing
    - Drawdown only applies if gains existed
    """

    name = "performance"

    def __init__(self, *, thresholds: dict, weight: float = 1.0):
        self.thresholds = thresholds
        self.weight = weight

    def evaluate(self, *, inputs: dict) -> HealthDimensionScore:
        returns = inputs.get("returns", [])

        # ---- No trades = no evidence ----
        if not returns:
            return HealthDimensionScore(
                name=self.name,
                score=0.0,
                weight=self.weight,
                metrics={},
                verdict=DimensionVerdict.FAIL,
            )

        avg_return = mean(returns)
        win_rate = sum(1 for r in returns if r > 0) / len(returns)

        std = pstdev(returns)
        sharpe = avg_return / std if std > 0 else 0.0

        # ---- Equity curve & drawdown ----
        equity = 0.0
        peak = 0.0
        max_dd = 0.0

        for r in returns:
            equity += r
            peak = max(peak, equity)
            max_dd = min(max_dd, equity - peak)

        min_peak = self.thresholds.get("min_peak_equity", 0.01)

        if peak <= min_peak:
            drawdown_pct = 0.0
        else:
            drawdown_pct = abs(max_dd) / peak

        # ---- Normalized component scores ----
        sharpe_score = min(
            max(sharpe / self.thresholds["sharpe_good"], 0.0),
            1.0,
        )

        win_rate_score = min(
            max(win_rate / self.thresholds["win_rate_good"], 0.0),
            1.0,
        )

        drawdown_score = max(
            0.0,
            1.0 - (drawdown_pct / self.thresholds["drawdown_bad"]),
        )

        raw_score = round(
            (sharpe_score + win_rate_score + drawdown_score) / 3.0,
            4,
        )

        # ---- VERDICT (ORDER MATTERS) ----
        if avg_return < 0 and win_rate < (self.thresholds["win_rate_good"] / 2):
            verdict = DimensionVerdict.FAIL

        elif peak > min_peak and drawdown_pct >= self.thresholds["drawdown_bad"]:
            verdict = DimensionVerdict.FAIL

        elif sharpe < self.thresholds["sharpe_warn"]:
            verdict = DimensionVerdict.WARN

        else:
            verdict = DimensionVerdict.PASS

        # ---- FAIL SCORE CAP (CRITICAL GOVERNANCE RULE) ----
        if verdict == DimensionVerdict.FAIL:
            score = min(raw_score, self.thresholds.get("fail_score_cap", 0.25))
        else:
            score = raw_score

        return HealthDimensionScore(
            name=self.name,
            score=score,
            weight=self.weight,
            metrics={
                "avg_return": round(avg_return, 6),
                "win_rate": round(win_rate, 4),
                "sharpe": round(sharpe, 4),
                "max_drawdown_pct": round(drawdown_pct, 4),
                "peak_equity": round(peak, 6),
            },
            verdict=verdict,
        )
