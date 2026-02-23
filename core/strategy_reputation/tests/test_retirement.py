from core.strategy_reputation.reputation import StrategyReputation
from core.strategy_reputation.normalization import NormalizedReputation
from core.strategy_reputation.retirement import (
    decide_strategy_retirement,
    StrategyLifecycleState,
)


def test_young_strategy_not_retired():
    rep = StrategyReputation("s1", cycles=2, total_pnl=-50.0, avg_sharpe=-0.5, worst_drawdown=0.4)
    norm = NormalizedReputation("s1", confidence=0.9, stability_penalty=0.8, normalized_score=-100.0)

    decision = decide_strategy_retirement(rep, norm)

    assert decision.state == StrategyLifecycleState.ACTIVE
    assert "insufficient career length" in decision.reason


def test_sustained_underperformance_triggers_retirement():
    rep = StrategyReputation("s1", cycles=6, total_pnl=-300.0, avg_sharpe=-0.8, worst_drawdown=0.6)
    norm = NormalizedReputation("s1", confidence=0.8, stability_penalty=0.7, normalized_score=-50.0)

    decision = decide_strategy_retirement(rep, norm)

    assert decision.state == StrategyLifecycleState.RETIRED
    assert "underperformance" in decision.reason


def test_recovering_strategy_not_retired():
    rep = StrategyReputation("s1", cycles=6, total_pnl=20.0, avg_sharpe=0.4, worst_drawdown=0.3)
    norm = NormalizedReputation("s1", confidence=0.8, stability_penalty=0.2, normalized_score=5.0)

    decision = decide_strategy_retirement(rep, norm)

    assert decision.state == StrategyLifecycleState.ACTIVE
