from .models import PortfolioRegimeState


def derive_portfolio_regime_state(
    portfolio_id: str,
    global_state,
    portfolio_volatility_ratio: float,
    concentration_index: float,
    fragility_score: float,
) -> PortfolioRegimeState:

    transition = min(
        1.0,
        global_state.transition_score +
        0.2 * portfolio_volatility_ratio +
        0.2 * fragility_score
    )

    break_score = min(
        1.0,
        global_state.structural_break_score +
        0.2 * concentration_index
    )

    stability = 1.0 - transition

    duration_weight = min(1.0, global_state.duration_cycles / 20.0)

    confidence = (
        0.4 * stability +
        0.3 * duration_weight +
        0.3 * (1.0 - break_score)
    )

    return PortfolioRegimeState(
        portfolio_id=portfolio_id,
        derived_from_global_label=global_state.regime_label,
        duration_cycles=global_state.duration_cycles,
        age_bucket=global_state.age_bucket,
        portfolio_transition_score=transition,
        portfolio_stability_score=stability,
        portfolio_break_score=break_score,
        portfolio_confidence_score=confidence,
    )