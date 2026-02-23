# test_phase11_eligibility_contract.py

from core.strategy_factory.promotion.promotion_decision import PromotionDecision

def test_promotion_decision_is_descriptive():
    decision = PromotionDecision(
        strategy_id="STRAT_001",
        eligible=True,
        reasons=["SSR above threshold"],
    )

    assert decision.strategy_id == "STRAT_001"
    assert decision.eligible is True
    assert isinstance(decision.reasons, list)
