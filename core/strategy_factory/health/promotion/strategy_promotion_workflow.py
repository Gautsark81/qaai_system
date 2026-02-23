from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from core.strategy_factory.health.lifecycle.strategy_lifecycle_controller import (
    StrategyLifecycleAction,
)


class PromotionDecisionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"


@dataclass(frozen=True)
class PromotionDecision:
    """
    Immutable, advisory-only promotion decision.
    """

    decision_id: str
    strategy_id: str
    proposed_action: StrategyLifecycleAction
    proposed_at: datetime

    decision_status: PromotionDecisionStatus
    decided_by: Optional[str]
    decided_at: Optional[datetime]
    reason: Optional[str]

    advisory_only: bool = field(init=False, default=True)


class StrategyPromotionWorkflow:
    """
    Human-in-the-loop promotion workflow.

    - No execution
    - No capital
    - Append-only decisions
    """

    def __init__(self):
        self._decisions: Dict[str, PromotionDecision] = {}
        self._active_pending: Dict[str, str] = {}

    # ----------------------------
    # Proposal
    # ----------------------------

    def propose_promotion(
        self,
        *,
        strategy_id: str,
        proposed_action: StrategyLifecycleAction,
        proposed_at: datetime,
    ) -> PromotionDecision:
        if proposed_action != StrategyLifecycleAction.PROMOTE:
            raise ValueError("Only PROMOTE actions may enter promotion workflow")

        if strategy_id in self._active_pending:
            raise ValueError(
                f"Strategy {strategy_id} already has a pending promotion decision"
            )

        decision_id = str(uuid.uuid4())

        decision = PromotionDecision(
            decision_id=decision_id,
            strategy_id=strategy_id,
            proposed_action=proposed_action,
            proposed_at=proposed_at,
            decision_status=PromotionDecisionStatus.PENDING,
            decided_by=None,
            decided_at=None,
            reason=None,
        )

        self._decisions[decision_id] = decision
        self._active_pending[strategy_id] = decision_id

        return decision

    # ----------------------------
    # Decision
    # ----------------------------

    def decide(
        self,
        *,
        decision_id: str,
        status: PromotionDecisionStatus,
        decided_by: str,
        reason: str,
        decided_at: datetime,
    ) -> PromotionDecision:
        if decision_id not in self._decisions:
            raise ValueError("Unknown decision_id")

        current = self._decisions[decision_id]

        if current.decision_status != PromotionDecisionStatus.PENDING:
            raise ValueError("Decision already finalized")

        updated = PromotionDecision(
            decision_id=current.decision_id,
            strategy_id=current.strategy_id,
            proposed_action=current.proposed_action,
            proposed_at=current.proposed_at,
            decision_status=status,
            decided_by=decided_by,
            decided_at=decided_at,
            reason=reason,
        )

        self._decisions[decision_id] = updated
        self._active_pending.pop(current.strategy_id, None)

        return updated
