# core/capital/contracts/__init__.py
#
# CANONICAL PUBLIC SURFACE FOR CAPITAL CONTRACTS
#
# Rules:
# - Only pure dataclasses / enums
# - No allocator, execution, or runtime logic
# - Stable import surface (tests depend on this)

from dataclasses import dataclass
from typing import Optional, Dict

from .fitness import CapitalFitness
from .context import CapitalDecisionContext
from .decision_snapshot import CapitalDecisionSnapshot


# ======================================================
# 🧾 STRATEGY CAPITAL SIGNAL
# ======================================================
#
# NOTE:
# This is duplicated here intentionally because:
# - core/capital/contracts.py (module) is shadowed by this package
# - Tests and emitters import from core.capital.contracts
#

@dataclass(frozen=True)
class StrategyCapitalSignal:
    """
    Read-only signal produced by Strategy / Meta / Phase-B layers.
    """
    ssr: float
    confidence: float
    regime_score: float


# ======================================================
# 🧾 CAPITAL EVIDENCE CONTEXT
# ======================================================

@dataclass(frozen=True)
class CapitalEvidenceContext:
    """
    Optional enrichment context for capital-related evidence.

    Evidence-only.
    Never feeds back into allocation logic.
    """
    capital_available: Optional[float] = None
    allocation_version: str = "v3"


__all__ = [
    "CapitalFitness",
    "CapitalDecisionContext",
    "CapitalDecisionSnapshot",
    "StrategyCapitalSignal",
    "CapitalEvidenceContext",
]
