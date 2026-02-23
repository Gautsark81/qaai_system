from statistics import mean, pstdev

from core.strategy_health.contracts.dimension import HealthDimensionScore
from core.strategy_health.contracts.enums import DimensionVerdict


class RiskBehaviorDimensionEvaluator:
    """
    Evaluates whether a strategy respects capital and risk discipline.

    GOVERNANCE-FIRST:
    - Risk breaches dominate
    - Tail loss considers ONLY losing trades
    - Risk volatility considers dispersion AND range
    - Backward-compatible threshold handling
    """

    name = "risk_behavior"

    def __init__(self, *, thresholds: dict, weight: float = 1.0):
        self.thresholds = thresholds
        self.weight = weight

    def evaluate(self, *, inputs: dict) -> HealthDimensionScore:
        risk_per_trade = inputs.get("risk_per_trade", [])
        trade_pnl = inputs.get("trade_pnl", [])
        risk_breaches = int(inputs.get("risk_breaches", 0))

        # ---- No evidence ----
        if not risk_per_trade:
            return HealthDimensionScore(
                name=self.name,
                score=0.0,
                weight=self.weight,
                metrics={},
                verdict=DimensionVerdict.FAIL,
            )

        avg_risk = mean(risk_per_trade)
        risk_vol = pstdev(risk_per_trade) if len(risk_per_trade) > 1 else 0.0
        risk_range = max(risk_per_trade) - min(risk_per_trade)

        # ---- Tail loss: ONLY negative trades ----
        losses = [p for p in trade_pnl if p < 0]
        worst_n = self.thresholds["tail_n"]
        worst_losses = sorted(losses)[:worst_n]
        tail_loss = abs(sum(worst_losses)) if worst_losses else 0.0

        # ---- Derived / backward-compatible thresholds ----
        max_avg_risk = self.thresholds["max_avg_risk"]
        risk_range_warn = self.thresholds.get(
            "risk_range_warn",
            0.75 * max_avg_risk,   # DEFAULT (governance-safe)
        )

        # ---- Normalized scores ----
        risk_score = max(
            0.0,
            1.0 - (avg_risk / max_avg_risk),
        )

        volatility_score = max(
            0.0,
            1.0 - (risk_vol / self.thresholds["risk_volatility_bad"]),
        )

        tail_score = max(
            0.0,
            1.0 - (tail_loss / self.thresholds["tail_loss_bad"]),
        )

        raw_score = round((risk_score + volatility_score + tail_score) / 3.0, 4)

        # ---- VERDICT (HARD LAW) ----
        if risk_breaches > 0:
            verdict = DimensionVerdict.FAIL

        elif avg_risk >= max_avg_risk:
            verdict = DimensionVerdict.FAIL

        elif tail_loss >= self.thresholds["tail_loss_bad"]:
            verdict = DimensionVerdict.FAIL

        elif (
            avg_risk >= self.thresholds["warn_avg_risk"]
            or risk_vol >= self.thresholds["risk_volatility_warn"]
            or risk_range >= risk_range_warn
        ):
            verdict = DimensionVerdict.WARN

        else:
            verdict = DimensionVerdict.PASS

        # ---- FAIL score cap ----
        if verdict == DimensionVerdict.FAIL:
            score = min(raw_score, self.thresholds.get("fail_score_cap", 0.25))
        else:
            score = raw_score

        return HealthDimensionScore(
            name=self.name,
            score=score,
            weight=self.weight,
            metrics={
                "avg_risk": round(avg_risk, 6),
                "risk_volatility": round(risk_vol, 6),
                "risk_range": round(risk_range, 6),
                "tail_loss": round(tail_loss, 6),
                "risk_breaches": risk_breaches,
            },
            verdict=verdict,
        )
