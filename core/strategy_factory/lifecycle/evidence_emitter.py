# core/strategy_factory/lifecycle/evidence_emitter.py

from typing import Tuple
from datetime import datetime, timezone

from core.evidence.decision_store import DecisionEvidenceStore
from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.checksum import compute_checksum

from core.strategy_factory.lifecycle.evidence_contracts import (
    LifecycleTransitionEvidence,
)


# ======================================================
# 🧾 LIFECYCLE TRANSITION EVIDENCE EMITTER
# ======================================================

def emit_lifecycle_transition_evidence(
    *,
    evidence: LifecycleTransitionEvidence,
    store: DecisionEvidenceStore,
) -> None:
    """
    Emit lifecycle transition evidence.

    Guarantees:
    - No lifecycle logic
    - No mutation
    - No exceptions raised
    - Deterministic checksum
    """

    factors: Tuple[tuple, ...] = (
        ("strategy_id", evidence.strategy_id),
        ("from_state", evidence.from_state.value),
        ("to_state", evidence.to_state.value),
        ("reason", evidence.reason),
        ("transition_id", evidence.transition_id),
    )

    # ✅ Deterministic checksum (timestamp NOT included)
    checksum = compute_checksum(fields=factors)

    store.append(
        DecisionEvidence(
            decision_id=checksum,
            decision_type="LIFECYCLE_TRANSITION",
            timestamp=datetime.now(timezone.utc),
            strategy_id=evidence.strategy_id,
            approved_weight=None,
            rationale=evidence.reason or "Lifecycle transition",
            factors=factors,
            checksum=checksum,
        )
    )
