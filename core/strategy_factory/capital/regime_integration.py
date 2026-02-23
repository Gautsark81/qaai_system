from dataclasses import dataclass

from core.regime.state_machine.models import PortfolioRegimeState


def _clip(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)


@dataclass(frozen=True)
class RegimeCapitalContext:
    multiplier: float
    freeze_new_allocations: bool
    regime_confidence: float
    structural_break_score: float


def compute_regime_capital_context(
    portfolio_regime_state: PortfolioRegimeState,
) -> RegimeCapitalContext:
    """
    Deterministic advisory capital context derived from portfolio regime state.

    This function:
    - Does NOT override governance
    - Does NOT override risk rules
    - Only provides advisory multiplier + freeze flag
    """

    confidence = portfolio_regime_state.portfolio_confidence_score
    break_score = portfolio_regime_state.portfolio_break_score
    transition = portfolio_regime_state.portfolio_transition_score
    age_bucket = portfolio_regime_state.age_bucket

    freeze = False
    multiplier = 1.0

    # 1️⃣ Structural Break Freeze
    if break_score >= 0.7:
        freeze = True
        multiplier = 0.0

    # 2️⃣ Low Confidence Dampening
    elif confidence < 0.4:
        multiplier = 0.5

    # 3️⃣ Early / High Transition Dampening
    elif transition > 0.6:
        multiplier = 0.7

    # 4️⃣ Late Cycle Slight Caution
    elif age_bucket == "late" and confidence < 0.75:
        multiplier = 0.85

    else:
        multiplier = 1.0

    return RegimeCapitalContext(
        multiplier=_clip(multiplier),
        freeze_new_allocations=freeze,
        regime_confidence=_clip(confidence),
        structural_break_score=_clip(break_score),
    )