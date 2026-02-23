from modules.intelligence.health import StrategyHealthEvaluator
from modules.intelligence.promotion import PromotionEvaluator
from modules.tournament.promotion_queue import PromotionRequest


class TournamentPromotionGate:
    def __init__(self, ssr_threshold: float = 0.8):
        self.health_eval = StrategyHealthEvaluator()
        self.promotion_eval = PromotionEvaluator()
        self.ssr_threshold = ssr_threshold

    def evaluate(
        self,
        strategy_id: str,
        ssr: float,
        metrics,
        stage: str = "PAPER",
    ):
        health = self.health_eval.evaluate(metrics)

        decision = self.promotion_eval.evaluate(
            ssr=ssr,
            health=health.health,
            threshold=self.ssr_threshold,
        )

        if not decision.eligible:
            return None

        return PromotionRequest(
            strategy_id=strategy_id,
            stage=stage,
            reason=decision.reason,
        )
