from intelligence.governance.promotion_rules import PromotionRules

class DummySnapshot:
    def __init__(self, ssr, trades, dd):
        self.ssr = ssr
        self.total_trades = trades
        self.max_drawdown = dd


def test_promotion_pass():
    snap = DummySnapshot(0.85, 50, 0.10)
    decision = PromotionRules.backtest_to_paper(snap)
    assert decision.eligible is True


def test_promotion_fail_ssr():
    snap = DummySnapshot(0.60, 50, 0.10)
    decision = PromotionRules.backtest_to_paper(snap)
    assert decision.eligible is False
