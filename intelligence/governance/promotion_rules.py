class PromotionDecision:
    def __init__(self, eligible: bool, reason: str):
        self.eligible = eligible
        self.reason = reason


class PromotionRules:
    @staticmethod
    def backtest_to_paper(snapshot) -> PromotionDecision:
        if snapshot.ssr < 0.80:
            return PromotionDecision(False, "SSR below threshold")
        if snapshot.total_trades < 30:
            return PromotionDecision(False, "Insufficient trades")
        if snapshot.max_drawdown > 0.25:
            return PromotionDecision(False, "Drawdown too high")
        return PromotionDecision(True, "Eligible for paper trading")
