from core.strategy_factory.promotion.state_machine.promotion_transition import PromotionTransition
from core.strategy_factory.promotion.state_machine.promotion_state import PromotionState


def test_promotion_transition_is_immutable_and_descriptive():
    t = PromotionTransition(
        from_state=PromotionState.SHADOW,
        to_state=PromotionState.PAPER,
        reason="SSR threshold met",
    )

    assert t.from_state == PromotionState.SHADOW
    assert t.to_state == PromotionState.PAPER
    assert isinstance(t.reason, str)
