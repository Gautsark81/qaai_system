from core.strategy_factory.promotion.state_machine.promotion_state_machine import PromotionStateMachine
from core.strategy_factory.promotion.state_machine.promotion_state import PromotionState


def test_invalid_promotion_transitions():
    sm = PromotionStateMachine()

    # No skipping
    assert not sm.can_transition(PromotionState.SHADOW, PromotionState.TINY_LIVE)

    # No backward
    assert not sm.can_transition(PromotionState.PAPER, PromotionState.SHADOW)

    # No self-loop
    assert not sm.can_transition(PromotionState.LIVE, PromotionState.LIVE)
