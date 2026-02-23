from core.strategy_factory.health.retirement.retirement_state import RetirementState

def test_states_exist():
    assert RetirementState.ACTIVE
    assert RetirementState.RETIRED
