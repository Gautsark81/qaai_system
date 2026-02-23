from modules.promotion.promotion_gate import PromotionGate


class Stats:
    paper_days = 40
    win_rate = 0.82
    max_drawdown = 0.04
    health_score = 0.8
    no_risk_violations = True


def test_promotion_gate_accepts():
    gate = PromotionGate()
    assert gate.eligible(stats=Stats)


def test_promotion_gate_rejects_low_winrate():
    gate = PromotionGate()
    Stats.win_rate = 0.6
    assert not gate.eligible(stats=Stats)
