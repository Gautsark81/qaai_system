from __future__ import annotations

from typing import Dict

from core.screening.snapshot import MarketSnapshot


class ScreeningScorer:
    """
    Deterministic scoring engine.

    IMPORTANT CONTRACT:
    - Pure function
    - No filtering
    - No side effects
    - No external state
    """

    def score(self, snap: MarketSnapshot) -> float:
        """
        Returns a signed score used ONLY for ranking.

        Positive → long bias
        Negative → short bias
        Magnitude → conviction
        """

        score = 0.0

        # -------- Trend component --------
        if snap.features and "trend_strength" in snap.features:
            score += float(snap.features["trend_strength"])
        else:
            if snap.atr and snap.atr > 0:
                score += (snap.close / snap.atr) * 0.01

        # -------- Volatility penalty --------
        if snap.volatility and snap.volatility > 0:
            score /= (1.0 + snap.volatility)

        return float(score)


# ==========================================================
# FUNCTIONAL API — REQUIRED BY TESTS
# ==========================================================

def score_rules(rules: Dict[str, Dict]) -> float:
    """
    Functional rule scoring helper.

    Expected input:
    {
        rule_name: {
            "passed": bool,
            "weight": float
        }
    }

    Output:
    Normalized score in range [0.0, 1.0]
    """

    if not rules:
        return 0.0

    total_weight = 0.0
    passed_weight = 0.0

    for meta in rules.values():
        weight = float(meta.get("weight", 0.0))
        total_weight += weight

        if meta.get("passed", False):
            passed_weight += weight

    if total_weight <= 0.0:
        return 0.0

    return float(passed_weight / total_weight)
