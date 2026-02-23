from core.strategy_factory.promotion.wiring.wiring_recommendation import (
    WiringRecommendation,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)


def test_wiring_recommendation_is_descriptive_only():
    rec = WiringRecommendation(
        strategy_id="STRAT_001",
        from_state=PromotionState.SHADOW,
        to_state=PromotionState.PAPER,
        reason="SSR threshold satisfied",
    )

    assert rec.strategy_id == "STRAT_001"
    assert rec.from_state == PromotionState.SHADOW
    assert rec.to_state == PromotionState.PAPER
    assert isinstance(rec.reason, str)
