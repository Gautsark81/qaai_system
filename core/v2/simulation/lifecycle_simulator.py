from __future__ import annotations
from .contracts import LifecycleDecision, LifecycleOutcome, CapitalSnapshot


class LifecycleSimulator:
    """
    Governance rules for strategy survival.
    """

    MAX_DRAWDOWN = 0.25
    MIN_PNL = 0.0

    def evaluate(self, snapshot: CapitalSnapshot) -> LifecycleOutcome:
        if snapshot.max_drawdown >= self.MAX_DRAWDOWN:
            return LifecycleOutcome(
                decision=LifecycleDecision.KILL,
                reason="Max drawdown exceeded",
            )

        if snapshot.pnl < self.MIN_PNL:
            return LifecycleOutcome(
                decision=LifecycleDecision.PAUSE,
                reason="Negative PnL",
            )

        return LifecycleOutcome(
            decision=LifecycleDecision.CONTINUE,
            reason="Capital healthy",
        )
