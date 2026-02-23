# test_phase11_no_capital_authority.py

from core.strategy_factory.promotion.promotion_decision import PromotionDecision

def test_promotion_decision_cannot_allocate_capital():
    decision = PromotionDecision(
        strategy_id="STRAT_002",
        eligible=True,
        reasons=[],
    )

    forbidden = {"capital", "allocation", "position_size"}
    assert forbidden.isdisjoint(vars(decision))
