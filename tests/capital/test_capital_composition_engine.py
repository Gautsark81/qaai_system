from core.capital.composition.engine import CapitalCompositionEngine


def test_risk_dominates_lifecycle():
    result = CapitalCompositionEngine.compose(
        requested_capital=100_000,
        risk_allowed_capital=10_000,
        lifecycle_multiplier=0.8,
        strategy_cap=50_000,
        account_available_capital=100_000,
    )
    assert result.final == 10_000


def test_lifecycle_reduces_capital():
    result = CapitalCompositionEngine.compose(
        requested_capital=100_000,
        risk_allowed_capital=100_000,
        lifecycle_multiplier=0.5,
        strategy_cap=100_000,
        account_available_capital=100_000,
    )
    assert result.final == 50_000


def test_strategy_cap_enforced():
    result = CapitalCompositionEngine.compose(
        requested_capital=100_000,
        risk_allowed_capital=100_000,
        lifecycle_multiplier=1.0,
        strategy_cap=20_000,
        account_available_capital=100_000,
    )
    assert result.final == 20_000


def test_account_cap_enforced():
    result = CapitalCompositionEngine.compose(
        requested_capital=100_000,
        risk_allowed_capital=100_000,
        lifecycle_multiplier=1.0,
        strategy_cap=100_000,
        account_available_capital=15_000,
    )
    assert result.final == 15_000


def test_any_zero_input_results_in_zero():
    result = CapitalCompositionEngine.compose(
        requested_capital=0,
        risk_allowed_capital=100_000,
        lifecycle_multiplier=1.0,
        strategy_cap=100_000,
        account_available_capital=100_000,
    )
    assert result.final == 0


def test_deterministic_output():
    r1 = CapitalCompositionEngine.compose(
        requested_capital=50_000,
        risk_allowed_capital=40_000,
        lifecycle_multiplier=0.9,
        strategy_cap=100_000,
        account_available_capital=100_000,
    )
    r2 = CapitalCompositionEngine.compose(
        requested_capital=50_000,
        risk_allowed_capital=40_000,
        lifecycle_multiplier=0.9,
        strategy_cap=100_000,
        account_available_capital=100_000,
    )
    assert r1 == r2
