from core.strategy_health.contracts.dimension import HealthDimensionScore
from core.strategy_health.contracts.enums import DimensionVerdict


class DataIntegrityDimensionEvaluator:
    """
    Evaluates whether incoming market / execution data is trustworthy.

    GOVERNANCE-FIRST:
    - Broken data invalidates all intelligence
    - FAILs are immediately visible (score cap)
    - Deterministic, threshold-driven
    """

    name = "data_integrity"

    def __init__(self, *, thresholds: dict, weight: float = 1.0):
        self.thresholds = thresholds
        self.weight = weight

    def evaluate(self, *, inputs: dict) -> HealthDimensionScore:
        missing_ratio = float(inputs.get("missing_ratio", 1.0))
        stale_ratio = float(inputs.get("stale_ratio", 1.0))
        outlier_ratio = float(inputs.get("outlier_ratio", 0.0))
        clock_skew_ms = float(inputs.get("clock_skew_ms", 0.0))
        provider_errors = int(inputs.get("provider_errors", 0))

        # ---- Normalized scores ----
        missing_score = max(
            0.0,
            1.0 - (missing_ratio / self.thresholds["missing_bad"]),
        )

        stale_score = max(
            0.0,
            1.0 - (stale_ratio / self.thresholds["stale_bad"]),
        )

        outlier_score = max(
            0.0,
            1.0 - (outlier_ratio / self.thresholds["outlier_bad"]),
        )

        skew_score = max(
            0.0,
            1.0 - (clock_skew_ms / self.thresholds["clock_skew_bad_ms"]),
        )

        raw_score = round(
            (missing_score + stale_score + outlier_score + skew_score) / 4.0,
            4,
        )

        # ---- VERDICT (HARD LAW) ----
        if missing_ratio >= self.thresholds["missing_bad"]:
            verdict = DimensionVerdict.FAIL

        elif stale_ratio >= self.thresholds["stale_bad"]:
            verdict = DimensionVerdict.FAIL

        elif clock_skew_ms >= self.thresholds["clock_skew_bad_ms"]:
            verdict = DimensionVerdict.FAIL

        elif provider_errors >= self.thresholds["provider_errors_bad"]:
            verdict = DimensionVerdict.FAIL

        elif (
            missing_ratio >= self.thresholds["missing_warn"]
            or stale_ratio >= self.thresholds["stale_warn"]
            or outlier_ratio >= self.thresholds["outlier_warn"]
            or clock_skew_ms >= self.thresholds["clock_skew_warn_ms"]
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
                "missing_ratio": round(missing_ratio, 4),
                "stale_ratio": round(stale_ratio, 4),
                "outlier_ratio": round(outlier_ratio, 4),
                "clock_skew_ms": round(clock_skew_ms, 2),
                "provider_errors": provider_errors,
            },
            verdict=verdict,
        )
