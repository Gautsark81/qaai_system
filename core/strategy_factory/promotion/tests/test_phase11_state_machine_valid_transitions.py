from core.strategy_factory.promotion.state_machine.promotion_state_machine import PromotionStateMachine
from core.strategy_factory.promotion.state_machine.promotion_state import PromotionState


def test_valid_promotion_transitions():
    sm = PromotionStateMachine()

    assert sm.can_transition(PromotionState.SHADOW, PromotionState.PAPER)
    assert sm.can_transition(PromotionState.PAPER, PromotionState.TINY_LIVE)
    assert sm.can_transition(PromotionState.TINY_LIVE, PromotionState.LIVE)
