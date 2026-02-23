# core/strategy_factory/strategy_generator.py

from uuid import uuid4
from typing import List, Dict
from core.strategy_factory.strategy_candidate import StrategyCandidate
from core.strategy_factory.probability_map import ProbabilityMap
from core.strategy_factory.elite_intraday_rules import EliteIntradayRules


class StrategyGenerator:
    """
    Generates ELITE intraday strategy candidates.
    """

    VERSION = "elite_intraday_v1"

    def generate(
        self,
        symbol_contexts: Dict[str, dict],
    ) -> List[StrategyCandidate]:

        candidates: List[StrategyCandidate] = []

        for symbol, ctx in symbol_contexts.items():
            zone_ok = (
                EliteIntradayRules.is_buy_zone(ctx) or
                EliteIntradayRules.is_sell_zone(ctx)
            )

            if not zone_ok:
                continue

            evaluation = ProbabilityMap.evaluate(ctx)

            if not evaluation["passed"]:
                continue

            candidate = StrategyCandidate(
                strategy_id=f"{symbol}_{uuid4().hex[:8]}",
                direction=ctx["trade_direction"],
                symbols=[symbol],
                probability_score=evaluation["score"],
                layers_passed=evaluation["layers"],
                rationale="All probability layers aligned",
                version=self.VERSION,
            )

            candidates.append(candidate)

        return candidates
