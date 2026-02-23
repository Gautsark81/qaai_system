from core.regime.state_machine.models import PortfolioRegimeState
from core.strategy_factory.capital.regime_integration import (
    compute_regime_capital_context,
)


def make_state(
    transition=0.2,
    break_score=0.0,
    confidence=0.8,
    age="mid",
):
    return PortfolioRegimeState(
        portfolio_id="P1",
        derived_from_global_label="BULL",
        duration_cycles=10,
        age_bucket=age,
        portfolio_transition_score=transition,
        portfolio_stability_score=1 - transition,
        portfolio_break_score=break_score,
        portfolio_confidence_score=confidence,
    )


def test_structural_break_freezes_allocation():
    state = make_state(break_score=0.8)
    ctx = compute_regime_capital_context(state)

    assert ctx.freeze_new_allocations is True
    assert ctx.multiplier == 0.0


def test_low_confidence_reduces_multiplier():
    state = make_state(confidence=0.3)
    ctx = compute_regime_capital_context(state)

    assert ctx.freeze_new_allocations is False
    assert ctx.multiplier == 0.5


def test_high_transition_dampens():
    state = make_state(transition=0.8, confidence=0.8)
    ctx = compute_regime_capital_context(state)

    assert ctx.multiplier == 0.7


def test_late_cycle_caution():
    state = make_state(age="late", confidence=0.6)
    ctx = compute_regime_capital_context(state)

    assert ctx.multiplier == 0.85


def test_stable_regime_full_scale():
    state = make_state()
    ctx = compute_regime_capital_context(state)

    assert ctx.freeze_new_allocations is False
    assert ctx.multiplier == 1.0