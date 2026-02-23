from collections import Counter

from core.strategy_health.contracts.dimension import HealthDimensionScore
from core.strategy_health.contracts.enums import DimensionVerdict


class RegimeFitDimensionEvaluator:
    """
    Evaluates whether a strategy is operating in its designed market regime.

    GOVERNANCE-FIRST:
    - Forbidden regime → FAIL
    - Persistent mismatch → FAIL
    - Recent transition into allowed regime → WARN
    - Instability → WARN
    """

    name = "regime_fit"

    def __init__(self, *, thresholds: dict, weight: float = 1.0):
        self.thresholds = thresholds
        self.weight = weight

    def evaluate(self, *, inputs: dict) -> HealthDimensionScore:
        allowed = set(inputs.get("allowed_regimes", set()))
        current = inputs.get("current_regime")
        history = list(inputs.get("recent_regime_history", []))

        # ---- No evidence ----
        if not allowed or not current:
            return HealthDimensionScore(
                name=self.name,
                score=0.0,
                weight=self.weight,
                metrics={},
                verdict=DimensionVerdict.FAIL,
            )

        # ---- Immediate forbidden regime ----
        if current not in allowed:
            return HealthDimensionScore(
                name=self.name,
                score=0.0,
                weight=self.weight,
                metrics={
                    "current_regime": current,
                    "allowed_regimes": list(allowed),
                },
                verdict=DimensionVerdict.FAIL,
            )

        # ---- History analysis ----
        window = history[-self.thresholds["history_window"] :] if history else []
        counts = Counter(window)
        total = len(window)

        mismatch_count = sum(
            c for r, c in counts.items() if r not in allowed
        )

        mismatch_ratio = (mismatch_count / total) if total > 0 else 0.0
        instability = len(counts)

        recent_mismatch_present = any(r not in allowed for r in window)

        # ---- Normalized score ----
        instability_ratio = (
            instability / self.thresholds["instability_bad"]
            if self.thresholds["instability_bad"] > 0
            else 0.0
        )

        raw_score = round(
            max(
                0.0,
                1.0 - max(mismatch_ratio, instability_ratio),
            ),
            4,
        )

        # ---- VERDICT (HARD LAW, ORDER MATTERS) ----
        if mismatch_ratio >= self.thresholds["mismatch_ratio_bad"]:
            verdict = DimensionVerdict.FAIL

        elif recent_mismatch_present:
            verdict = DimensionVerdict.WARN

        elif instability >= self.thresholds["instability_warn"]:
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
                "current_regime": current,
                "allowed_regimes": list(allowed),
                "mismatch_ratio": round(mismatch_ratio, 4),
                "instability": instability,
                "recent_transition": recent_mismatch_present,
            },
            verdict=verdict,
        )
