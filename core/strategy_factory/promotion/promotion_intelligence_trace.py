# core/strategy_factory/promotion/promotion_intelligence_trace.py

from __future__ import annotations

import hashlib
from dataclasses import dataclass


# ---------------------------------------------------------------------
# Promotion Intelligence Trace (C6.2)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class PromotionIntelligenceTrace:
    """
    C6.2 — Unified Promotion Intelligence Trace Artifact

    Binds:
        - Promotion Intelligence Score Artifact
        - Screening Governance Snapshot
        - Capital Governance Chain
        - Lifecycle State

    HARD GUARANTEES:
        - Deterministic
        - Immutable
        - Advisory only
        - No mutation authority
        - Hash reproducible
    """

    strategy_dna: str
    intelligence_hash: str
    screening_hash: str
    capital_governance_chain_id: str
    lifecycle_state: str
    composite_trace_hash: str


# ---------------------------------------------------------------------
# Deterministic Hash Builder
# ---------------------------------------------------------------------

def compute_promotion_trace_hash(
    *,
    strategy_dna: str,
    intelligence_hash: str,
    screening_hash: str,
    capital_governance_chain_id: str,
    lifecycle_state: str,
) -> str:
    """
    Deterministic composite hash of full promotion intelligence context.
    """

    payload = "|".join(
        [
            strategy_dna,
            intelligence_hash,
            screening_hash,
            capital_governance_chain_id,
            lifecycle_state,
        ]
    )

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------

def build_promotion_intelligence_trace(
    *,
    strategy_dna: str,
    intelligence_hash: str,
    screening_hash: str,
    capital_governance_chain_id: str,
    lifecycle_state: str,
) -> PromotionIntelligenceTrace:
    """
    Construct immutable promotion intelligence trace.
    """

    composite_hash = compute_promotion_trace_hash(
        strategy_dna=strategy_dna,
        intelligence_hash=intelligence_hash,
        screening_hash=screening_hash,
        capital_governance_chain_id=capital_governance_chain_id,
        lifecycle_state=lifecycle_state,
    )

    return PromotionIntelligenceTrace(
        strategy_dna=strategy_dna,
        intelligence_hash=intelligence_hash,
        screening_hash=screening_hash,
        capital_governance_chain_id=capital_governance_chain_id,
        lifecycle_state=lifecycle_state,
        composite_trace_hash=composite_hash,
    )