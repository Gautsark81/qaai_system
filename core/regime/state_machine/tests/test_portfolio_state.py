from core.regime.state_machine.models import GlobalRegimeState
from core.regime.state_machine.portfolio_derivation import derive_portfolio_regime_state


def test_portfolio_derivation_increases_transition():
    global_state = GlobalRegimeState(
        regime_label="BULL",
        start_cycle=1,
        current_cycle=10,
        duration_cycles=10,
        age_bucket="mid",
        transition_score=0.2,
        stability_score=0.8,
        structural_break_score=0.0,
        confidence_score=0.8,
    )

    portfolio_state = derive_portfolio_regime_state(
        portfolio_id="P1",
        global_state=global_state,
        portfolio_volatility_ratio=1.0,
        concentration_index=0.5,
        fragility_score=0.5,
    )

    assert portfolio_state.portfolio_transition_score >= global_state.transition_score