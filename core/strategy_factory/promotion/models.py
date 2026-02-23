from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional


class PromotionLevel(str, Enum):
    """
    Governance classification for strategy lifecycle eligibility.

    NOTE:
    - LIVE_ELIGIBLE does NOT mean deployed
    - No execution or capital authority is implied
    """

    REJECTED = "rejected"
    RESEARCH = "research"
    PAPER = "paper"
    LIVE_ELIGIBLE = "live_eligible"


@dataclass(frozen=True)
class PromotionPolicy:
    """
    Deterministic thresholds governing promotion decisions.

    Backward-compatible across C1.4-A and C1.4-B.
    """

    # --------------------------------------------------
    # Evidence requirements
    # --------------------------------------------------
    min_samples: int

    # --------------------------------------------------
    # SSR thresholds (research → paper → live)
    # --------------------------------------------------
    research_ssr: float
    paper_ssr: float
    live_ssr: float

    # --------------------------------------------------
    # Paper-trade confirmation (C1.4-B)
    # Defaults preserve C1.4-A behavior
    # --------------------------------------------------
    paper_confirm_ssr: float = 0.0
    paper_max_drawdown: float = 1.0

    # --------------------------------------------------
    # Risk limits
    # --------------------------------------------------
    max_drawdown: float = 1.0


@dataclass(frozen=True)
class PromotionDecision:
    """
    Output of promotion evaluation.

    Pure governance verdict with an explanatory reason.
    """

    level: PromotionLevel
    reason: str

@dataclass(frozen=True)
class PromotionAuditRecord:
    """
    Immutable audit record for a promotion decision.

    Captures decision context, evidence fingerprints,
    and creation time for lineage and explainability.
    """

    strategy_dna: str

    decision: PromotionDecision

    health_fingerprint: str
    policy_fingerprint: str
    paper_fingerprint: Optional[str]
    memory_fingerprint: Optional[str]

    created_at: datetime
