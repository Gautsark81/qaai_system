from core.strategy_factory.lifecycle.contracts import StrategyLifecycleState
from core.strategy_factory.promotion.models import PromotionLevel
from core.strategy_factory.health.models import StrategyHealthSnapshot
from core.strategy_factory.capital.decision import decide_capital_eligibility


def make_health(ssr=0.85, drawdown=0.10):
    return StrategyHealthSnapshot(
        ssr=ssr,
        total_trades=200,
        max_drawdown=drawdown,
        flags=set(),
    )


def test_capital_eligible_when_all_gates_pass():
    decision = decide_capital_eligibility(
        lifecycle_state=StrategyLifecycleState.LIVE,
        promotion_level=PromotionLevel.LIVE_ELIGIBLE,
        health=make_health(),
    )

    assert decision.eligible is True
    assert "eligible" in decision.reason.lower()


def test_reject_when_not_live_lifecycle():
    decision = decide_capital_eligibility(
        lifecycle_state=StrategyLifecycleState.PAPER,
        promotion_level=PromotionLevel.LIVE_ELIGIBLE,
        health=make_health(),
    )

    assert decision.eligible is False
    assert "lifecycle" in decision.reason.lower()


def test_reject_when_not_live_eligible_promotion():
    decision = decide_capital_eligibility(
        lifecycle_state=StrategyLifecycleState.LIVE,
        promotion_level=PromotionLevel.PAPER,
        health=make_health(),
    )

    assert decision.eligible is False
    assert "promotion" in decision.reason.lower()


def test_reject_when_health_ssr_too_low():
    decision = decide_capital_eligibility(
        lifecycle_state=StrategyLifecycleState.LIVE,
        promotion_level=PromotionLevel.LIVE_ELIGIBLE,
        health=make_health(ssr=0.60),
    )

    assert decision.eligible is False
    assert "ssr" in decision.reason.lower()


def test_reject_when_drawdown_too_high():
    decision = decide_capital_eligibility(
        lifecycle_state=StrategyLifecycleState.LIVE,
        promotion_level=PromotionLevel.LIVE_ELIGIBLE,
        health=make_health(drawdown=0.35),
    )

    assert decision.eligible is False
    assert "drawdown" in decision.reason.lower()
