from core.strategy_factory.promotion.state_machine.promotion_state_machine import PromotionStateMachine


def test_state_machine_has_no_side_effects():
    sm = PromotionStateMachine()

    for attr in dir(sm):
        assert "execute" not in attr
        assert "order" not in attr
        assert "capital" not in attr
        assert "arm" not in attr
