from statistics import mean, pstdev

from core.strategy_health.contracts.dimension import HealthDimensionScore
from core.strategy_health.contracts.enums import DimensionVerdict


class ExecutionQualityDimensionEvaluator:
    """
    Evaluates execution quality independent of strategy performance.

    GOVERNANCE-FIRST:
    - Rejects and severe slippage dominate
    - Latency spikes are penalized
    - FAIL verdicts are visibly bad (score cap)
    """

    name = "execution_quality"

    def __init__(self, *, thresholds: dict, weight: float = 1.0):
        self.thresholds = thresholds
        self.weight = weight

    def evaluate(self, *, inputs: dict) -> HealthDimensionScore:
        expected = inputs.get("expected_price", [])
        filled = inputs.get("fill_price", [])
        latency = inputs.get("latency_ms", [])

        rejected = int(inputs.get("rejected_orders", 0))
        total = int(inputs.get("total_orders", 0))
        partials = int(inputs.get("partial_fills", 0))

        # ---- No evidence ----
        if not expected or not filled or len(expected) != len(filled):
            return HealthDimensionScore(
                name=self.name,
                score=0.0,
                weight=self.weight,
                metrics={},
                verdict=DimensionVerdict.FAIL,
            )

        # ---- Slippage (absolute, normalized) ----
        slippages = [abs(f - e) for e, f in zip(expected, filled)]
        avg_slip = mean(slippages)
        tail_n = self.thresholds["tail_n"]
        tail_slip = mean(sorted(slippages, reverse=True)[:tail_n])

        # ---- Latency ----
        avg_latency = mean(latency) if latency else 0.0
        latency_vol = pstdev(latency) if len(latency) > 1 else 0.0
        max_latency = max(latency) if latency else 0.0

        # ---- Rates ----
        reject_rate = (rejected / total) if total > 0 else 0.0
        partial_rate = (partials / total) if total > 0 else 0.0

        # ---- Normalized scores ----
        slip_score = max(
            0.0,
            1.0 - (avg_slip / self.thresholds["avg_slippage_bad"]),
        )

        tail_slip_score = max(
            0.0,
            1.0 - (tail_slip / self.thresholds["tail_slippage_bad"]),
        )

        latency_score = max(
            0.0,
            1.0 - (avg_latency / self.thresholds["avg_latency_bad"]),
        )

        raw_score = round(
            (slip_score + tail_slip_score + latency_score) / 3.0,
            4,
        )

        # ---- VERDICT (HARD LAW) ----
        if reject_rate >= self.thresholds["reject_rate_bad"]:
            verdict = DimensionVerdict.FAIL

        elif avg_slip >= self.thresholds["avg_slippage_bad"]:
            verdict = DimensionVerdict.FAIL

        elif tail_slip >= self.thresholds["tail_slippage_bad"]:
            verdict = DimensionVerdict.FAIL

        elif partial_rate >= self.thresholds["partial_rate_bad"]:
            verdict = DimensionVerdict.FAIL

        elif max_latency >= self.thresholds["max_latency_bad"]:
            verdict = DimensionVerdict.FAIL

        elif (
            reject_rate >= self.thresholds["reject_rate_warn"]
            or avg_slip >= self.thresholds["avg_slippage_warn"]
            or latency_vol >= self.thresholds["latency_volatility_warn"]
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
                "avg_slippage": round(avg_slip, 6),
                "tail_slippage": round(tail_slip, 6),
                "avg_latency_ms": round(avg_latency, 2),
                "latency_volatility": round(latency_vol, 2),
                "max_latency_ms": round(max_latency, 2),
                "reject_rate": round(reject_rate, 4),
                "partial_rate": round(partial_rate, 4),
            },
            verdict=verdict,
        )
