from __future__ import annotations

from typing import List

from strategies.base import StrategySignal
from risk.base import RiskContextProtocol, RiskDecision
from risk.rules import RiskRule


class RiskEngine:
    """
    Runs a stack of RiskRule objects.

    Supercharged:
    - Each rule can annotate meta, and the final decision collects them.

    Hybrid:
    - Works identically in live and backtest (RiskContextProtocol abstraction).
    """

    def __init__(self, rules: List[RiskRule]) -> None:
        self._rules = rules

    def evaluate_signal(
        self,
        ctx: RiskContextProtocol,
        signal: StrategySignal,
    ) -> RiskDecision:
        size = signal.size
        combined_meta = {}

        for rule in self._rules:
            decision = rule.evaluate(ctx, signal)
            size = min(size, decision.adjusted_size)
            combined_meta[rule.name] = 1.0 if decision.approved else 0.0

            # merge rule meta
            for k, v in (decision.meta or {}).items():
                combined_meta[f"{rule.name}.{k}"] = float(v)

            if not decision.approved:
                return RiskDecision(
                    approved=False,
                    reason=decision.reason,
                    adjusted_size=0.0,
                    meta=combined_meta,
                )

        return RiskDecision(
            approved=size > 0,
            reason="OK" if size > 0 else "ZERO_SIZE",
            adjusted_size=size,
            meta=combined_meta,
        )
