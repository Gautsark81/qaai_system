# core/paper_trading/invariants.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from core.capital.allocator_v3.contracts import (
    CapitalDecisionArtifact,
    CapitalDecisionStatus,
    StrategyDecision,
)
from core.operations.arming import ExecutionArming, SystemArmingState


# ---------------------------------------------------------------------
# Phase 14.0 — Paper Trading Execution Invariant
# ---------------------------------------------------------------------

class PaperTradingInvariantViolation(Exception):
    """
    Raised when a paper-trading invariant is violated.

    Laws:
    - Deterministic
    - Side-effect free
    - Replay-safe
    - Paper-scope ONLY
    """
    pass


@dataclass(frozen=True)
class PaperExecutionInvariantGuard:
    """
    Phase 14.0 — Paper Execution Invariant Guard.

    Responsibilities:
    - Enforce execution arming for paper trading
    - Translate global arming state into paper-scoped authority
    - NEVER mutate state
    - NEVER decide execution logic
    """

    arming: ExecutionArming

    def enforce(self) -> None:
        if self.arming.state != SystemArmingState.ARMED:
            raise PaperTradingInvariantViolation(
                "Paper trading execution blocked: system is not armed"
            )


# ---------------------------------------------------------------------
# Paper Allocation Wrapper
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class PaperAllocation:
    allocated_fraction: float


# ---------------------------------------------------------------------
# Paper Capital Decision
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class PaperCapitalDecision:
    allocations: Dict[str, PaperAllocation]
    decisions: Dict[str, StrategyDecision]
    total_allocated: float
    status: CapitalDecisionStatus


# ---------------------------------------------------------------------
# Paper Capital Invariant Guard (EXISTING — PRESERVED)
# ---------------------------------------------------------------------

class PaperInvariantGuard:
    """
    Paper-trading–specific capital invariant enforcement.

    Responsibilities:
    - Wrap allocator outputs into paper-safe types
    - Enforce total allocation ≤ 1.0 (already enforced upstream)
    - Preserve allocator semantics exactly
    """

    def wrap_decision(
        self, decision: CapitalDecisionArtifact
    ) -> PaperCapitalDecision:
        allocations: Dict[str, PaperAllocation] = {}

        for strategy_id, alloc in decision.allocations.items():
            allocations[strategy_id] = PaperAllocation(
                allocated_fraction=alloc.allocated_fraction
            )

        return PaperCapitalDecision(
            allocations=allocations,
            decisions=decision.decisions,
            total_allocated=decision.total_allocated,
            status=decision.status,
        )
