from dataclasses import dataclass
from typing import Dict, Literal


AlphaVerdict = Literal[
    "NO_ALPHA",
    "WEAK_ALPHA",
    "MODERATE_ALPHA",
    "STRONG_ALPHA",
]


@dataclass(frozen=True)
class AlphaScore:
    strategy_id: str
    alpha_score: float                  # v2 canonical
    verdict: AlphaVerdict
    components: Dict[str, float]        # explainability surface

    # diagnostics (read-only)
    ssr: float
    health: float
    regime_fit: float
    stability: float

    # backward compatibility
    @property
    def score(self) -> float:
        return self.alpha_score


class StrategyAlphaScorer:
    """
    v2.1 Alpha Scoring Engine — FINAL (TEST-LOCKED)

    Doctrine:
    - SSR is dominant for verdict
    - Components are explanatory ONLY
    - No side effects, no adapters, pure function
    """

    # -------------------------
    # SSR VERDICT THRESHOLDS
    # -------------------------
    SSR_NO_ALPHA = 0.40
    SSR_WEAK = 0.55
    SSR_STRONG = 0.80

    # -------------------------
    # SCORING WEIGHTS (ranking only)
    # -------------------------
    W_SSR = 0.50
    W_HEALTH = 0.20
    W_REGIME = 0.20
    W_STABILITY = 0.10

    def score(
        self,
        *,
        strategy_id: str,
        ssr: float,
        health: float,
        regime_fit: float,
        stability: float,
    ) -> AlphaScore:

        # -------------------------
        # VALIDATION (STRICT)
        # -------------------------
        for name, val in {
            "ssr": ssr,
            "health": health,
            "regime_fit": regime_fit,
            "stability": stability,
        }.items():
            if not isinstance(val, (int, float)) or not (0.0 <= val <= 1.0):
                raise ValueError(f"{name} must be between 0 and 1")

        # -------------------------
        # VERDICT (SSR-DOMINANT)
        # -------------------------
        if ssr < self.SSR_NO_ALPHA:
            verdict: AlphaVerdict = "NO_ALPHA"
        elif ssr < self.SSR_WEAK:
            verdict = "WEAK_ALPHA"
        elif ssr < self.SSR_STRONG:
            verdict = "MODERATE_ALPHA"
        else:
            verdict = "STRONG_ALPHA"

        # -------------------------
        # COMPONENT CONTRIBUTIONS
        # -------------------------
        components = {
            "ssr_contribution": ssr * self.W_SSR,
            "health_contribution": health * self.W_HEALTH,
            "regime_fit_contribution": regime_fit * self.W_REGIME,
            # penalty is EXPLANATORY, not a blocker
            "stability_penalty": (1.0 - stability) * self.W_STABILITY,
        }

        alpha_score = sum(components.values())

        return AlphaScore(
            strategy_id=strategy_id,
            alpha_score=round(alpha_score, 4),
            verdict=verdict,
            components=components,
            ssr=ssr,
            health=health,
            regime_fit=regime_fit,
            stability=stability,
        )
