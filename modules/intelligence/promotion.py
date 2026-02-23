from dataclasses import dataclass
from .health import StrategyHealth
from .metrics import StrategyMetrics


@dataclass(frozen=True)
class PromotionDecision:
    eligible: bool
    reason: str


class PromotionEvaluator:
    def evaluate(
        self,
        ssr: float,
        health: StrategyHealth,
        threshold: float = 0.8,
    ) -> PromotionDecision:
        if health != StrategyHealth.HEALTHY:
            return PromotionDecision(False, "Strategy health not healthy")

        if ssr < threshold:
            return PromotionDecision(False, f"SSR below threshold ({ssr})")

        return PromotionDecision(True, "Eligible for next lifecycle stage")
