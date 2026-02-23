# core/strategy_factory/screening/screening_promotion_trace.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import hashlib


# -------------------------------------------------------------
# Immutable Trace Model
# -------------------------------------------------------------

@dataclass(frozen=True)
class ScreeningPromotionTrace:
    """
    C5.12 — Deterministic Screening → Promotion Trace Artifact

    HARD GUARANTEES:
    - Immutable
    - No authority
    - No lifecycle mutation
    - No capital mutation
    - No promotion execution
    - Deterministic hash linkage
    """

    screening_state_hash: str
    advisory_state_hash: str
    policy_fingerprint: str
    trace_hash: str


# -------------------------------------------------------------
# Deterministic Builder
# -------------------------------------------------------------

def build_screening_promotion_trace(
    *,
    screening_state_hash: str,
    advisory_state_hash: str,
    policy_params: Tuple[str, ...],
) -> ScreeningPromotionTrace:
    """
    Construct deterministic trace artifact.

    policy_params:
        Immutable tuple describing policy configuration
        (e.g. SSR threshold, regime tag, capital context label)
    """

    # Deterministic fingerprint of policy configuration
    policy_fingerprint = hashlib.sha256(
        "|".join(sorted(policy_params)).encode()
    ).hexdigest()

    # Deterministic trace hash
    trace_hash = hashlib.sha256(
        f"{screening_state_hash}|{advisory_state_hash}|{policy_fingerprint}".encode()
    ).hexdigest()

    return ScreeningPromotionTrace(
        screening_state_hash=screening_state_hash,
        advisory_state_hash=advisory_state_hash,
        policy_fingerprint=policy_fingerprint,
        trace_hash=trace_hash,
    )