from core.strategy_factory.promotion.state_machine.promotion_state import PromotionState


def test_promotion_states_are_explicit_and_locked():
    assert PromotionState.SHADOW.name == "SHADOW"
    assert PromotionState.PAPER.name == "PAPER"
    assert PromotionState.TINY_LIVE.name == "TINY_LIVE"
    assert PromotionState.LIVE.name == "LIVE"

    # No hidden states
    assert len(PromotionState) == 4
