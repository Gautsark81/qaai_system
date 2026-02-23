from typing import Dict


class SSREngine:
    """
    Pure Strategy Success Ratio (SSR) computation engine.

    Guarantees:
    - Deterministic
    - Stateless
    - No side effects
    - Output ∈ [0.0, 1.0]
    """

    DEFAULT_WEIGHTS = {
        "performance": 0.4,
        "risk": 0.3,
        "stability": 0.3,
    }

    @classmethod
    def compute(
        cls,
        *,
        components: Dict[str, float],
        weights: Dict[str, float] | None = None,
    ) -> float:
        """
        Compute SSR from component scores.

        Missing components are treated as zero.
        Extra components are ignored unless weighted.
        """

        w = weights or cls.DEFAULT_WEIGHTS

        total_weight = 0.0
        weighted_sum = 0.0

        for name, weight in w.items():
            score = float(components.get(name, 0.0))
            score = max(0.0, min(score, 1.0))  # clamp
            weighted_sum += score * weight
            total_weight += weight

        if total_weight <= 0.0:
            return 0.0

        ssr = weighted_sum / total_weight
        return round(max(0.0, min(ssr, 1.0)), 6)
