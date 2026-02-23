from modules.promotion.promotion_orchestrator import PromotionOrchestrator
from modules.promotion.promotion_state import PromotionState


class Stats:
    paper_days = 40
    win_rate = 0.85
    max_drawdown = 0.03
    health_score = 0.8
    no_risk_violations = True


def test_paper_to_candidate():
    orch = PromotionOrchestrator()

    state, cap = orch.step(
        current_state=PromotionState.PAPER,
        stats=Stats,
        live_days=0,
    )

    assert state == PromotionState.CANDIDATE
    assert cap == 0.0


def test_candidate_to_live():
    orch = PromotionOrchestrator()

    state, cap = orch.step(
        current_state=PromotionState.CANDIDATE,
        stats=Stats,
        live_days=10,
    )

    assert state == PromotionState.LIVE
    assert cap > 0
