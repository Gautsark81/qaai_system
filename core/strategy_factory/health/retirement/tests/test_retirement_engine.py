from core.strategy_factory.health.retirement.retirement_engine import (
    StrategyRetirementEngine,
)
from core.strategy_factory.health.retirement.retirement_state import RetirementState

def test_retirement_flow():
    engine = StrategyRetirementEngine()
    sid = "s1"

    r1 = engine.transition(
        sid,
        RetirementState.AT_RISK,
        reason="decay",
        trigger="policy",
        metrics={},
    )
    assert r1.to_state == RetirementState.AT_RISK

    r2 = engine.transition(
        sid,
        RetirementState.COOLING,
        reason="critical",
        trigger="policy",
        metrics={},
    )
    assert not engine.is_tradeable(sid)
