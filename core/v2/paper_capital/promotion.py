from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PromotionInput:
    strategy_id: str
    ssr: float
    stability_stddev: float
    regime_match: bool


@dataclass(frozen=True)
class PromotionDecision:
    strategy_id: str
    promoted: bool
    reasons: List[str]


class PromotionGate:
    """
    Governance gate for promoting strategies to paper capital.
    """

    def __init__(
        self,
        *,
        min_ssr: float = 0.8,
        max_stability_stddev: float = 0.5,
    ):
        self._min_ssr = min_ssr
        self._max_stability_stddev = max_stability_stddev

    def evaluate(self, inputs: List[PromotionInput]) -> List[PromotionDecision]:
        decisions: List[PromotionDecision] = []

        for i in inputs:
            reasons: List[str] = []
            promoted = True

            if i.ssr < self._min_ssr:
                promoted = False
                reasons.append(f"SSR<{self._min_ssr}")

            if i.stability_stddev > self._max_stability_stddev:
                promoted = False
                reasons.append(f"stability>{self._max_stability_stddev}")

            if not i.regime_match:
                promoted = False
                reasons.append("regime_mismatch")

            if promoted:
                reasons = [
                    f"SSR>={self._min_ssr}",
                    f"stability<={self._max_stability_stddev}",
                    "regime_match",
                ]

            decisions.append(
                PromotionDecision(
                    strategy_id=i.strategy_id,
                    promoted=promoted,
                    reasons=reasons,
                )
            )

        return decisions
