from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

# ======================================================
# 🧠 STRATEGY CAPITAL SIGNAL
# ======================================================

@dataclass(frozen=True)
class StrategyCapitalSignal:
    """
    Read-only signal produced by Strategy / Phase-B / Meta layer.
    """
    ssr: float
    confidence: float
    regime_score: float


# ======================================================
# 📊 CAPITAL ALLOCATION RESULT (LEGACY / SIMPLE)
# ======================================================

@dataclass(frozen=True)
class CapitalAllocationResult:
    """
    Pure allocation result.
    """
    weights: Dict[str, float]
    capital_available: float


# ======================================================
# 🧾 CAPITAL EVIDENCE CONTEXT (ADDITIVE, CANONICAL)
# ======================================================

@dataclass(frozen=True)
class CapitalEvidenceContext:
    """
    Optional enrichment context for capital-related evidence.

    Design rules:
    - NEVER affects allocation math
    - Used ONLY by evidence emitters
    - Safe to construct partially
    """

    capital_available: Optional[float] = None
    allocation_version: str = "v3"


# ======================================================
# 🔒 EXPLICIT EXPORTS (CRITICAL FOR IMPORT STABILITY)
# ======================================================

__all__ = [
    "StrategyCapitalSignal",
    "CapitalAllocationResult",
    "CapitalEvidenceContext",
]
