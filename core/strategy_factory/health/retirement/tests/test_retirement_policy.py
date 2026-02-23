from core.strategy_factory.health.retirement.retirement_policy import RetirementPolicy
from core.strategy_factory.health.retirement.retirement_state import RetirementState
from core.strategy_factory.health.decay.decay_state import AlphaDecayState

def test_critical_decay_triggers_cooling():
    policy = RetirementPolicy()
    next_state = policy.decide(
        RetirementState.ACTIVE, AlphaDecayState.CRITICAL, 0
    )
    assert next_state == RetirementState.COOLING
