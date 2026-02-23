# modules/operator_dashboard/governance_actions.py

"""
⚠️ PHASE F — GOVERNANCE INTENT EMISSION ONLY ⚠️

This module MUST NOT mutate system state.

It exists solely to:
- Express human governance intent
- Emit auditable, signed intent records
- Support UI workflows & simulations

Execution is handled OUTSIDE Phase F.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

# --- Evidence (read-only, optional) ---
from core.evidence.governance_binder import bind_governance_signature
from core.evidence.decision_store import DecisionEvidenceStore


# ======================================================
# GOVERNANCE INTENT CONTRACTS (READ-ONLY)
# ======================================================

class GovernanceAction(str, Enum):
    APPROVE_FOR_PAPER = "APPROVE_FOR_PAPER"
    REJECT_FOR_PAPER = "REJECT_FOR_PAPER"
    APPROVE_FOR_LIVE = "APPROVE_FOR_LIVE"
    REJECT_FOR_LIVE = "REJECT_FOR_LIVE"


@dataclass(frozen=True)
class GovernanceIntent:
    """
    Immutable governance intent emitted by an operator.

    This is NOT an approval.
    This is NOT authoritative.
    This is an auditable human signal only.
    """
    action: GovernanceAction
    run_id: str
    strategy_id: str
    reviewer: str
    reasons: List[str]
    emitted_at: datetime

    # Optional signed evidence reference (Phase F-1.2)
    signature: Optional[str] = None
    signature_algorithm: Optional[str] = None


# ======================================================
# INTERNAL: read-only signature emission (never required)
# ======================================================

def _emit_signed_intent_evidence(
    *,
    intent: GovernanceIntent,
) -> Optional[str]:
    """
    Bind a cryptographic signature to a governance intent.

    Guarantees:
    - NEVER raises
    - NEVER blocks intent emission
    - NEVER mutates system state
    """

    try:
        # NOTE:
        # In production, the secret MUST come from a secure runtime source
        # (env, vault, KMS). This placeholder is intentional & replaceable.
        secret = b"LOCAL_DEV_SECRET"

        signed = bind_governance_signature(
            decision_id=f"{intent.run_id}:{intent.strategy_id}:{intent.action.value}",
            governance_type=(
                "PAPER" if "PAPER" in intent.action.value else "LIVE"
            ),
            strategy_id=intent.strategy_id,
            status=intent.action.value,
            reasons=intent.reasons,
            reviewer=intent.reviewer,
            reviewer_fingerprint=intent.reviewer,  # replace with identity hash later
            decided_at=intent.emitted_at,
            decision_checksum=f"{intent.run_id}:{intent.strategy_id}",
            secret=secret,
        )

        # Append evidence (append-only, read-only)
        DecisionEvidenceStore().append(signed)

        return signed.signature

    except Exception:
        # Intent emission must NEVER fail due to evidence
        return None


# ======================================================
# INTENT EMISSION HELPERS (NO SIDE EFFECTS)
# ======================================================

def emit_governance_intent(
    *,
    action: GovernanceAction,
    run_id: str,
    strategy_id: str,
    reviewer: str,
    reasons: List[str],
) -> GovernanceIntent:
    """
    Emit a governance intent for review, logging, or external handling.

    ❌ Does NOT persist approvals
    ❌ Does NOT call core governance
    ❌ Does NOT change system state
    """

    emitted_at = datetime.now(timezone.utc)

    intent = GovernanceIntent(
        action=action,
        run_id=run_id,
        strategy_id=strategy_id,
        reviewer=reviewer,
        reasons=reasons,
        emitted_at=emitted_at,
    )

    # Optional signature binding (Phase F-1.2)
    signature = _emit_signed_intent_evidence(intent=intent)

    if signature:
        return GovernanceIntent(
            action=intent.action,
            run_id=intent.run_id,
            strategy_id=intent.strategy_id,
            reviewer=intent.reviewer,
            reasons=intent.reasons,
            emitted_at=intent.emitted_at,
            signature=signature,
            signature_algorithm="HMAC-SHA256",
        )

    return intent


# ------------------------------------------------------
# Convenience wrappers (UI-friendly, still safe)
# ------------------------------------------------------

def propose_approve_for_paper(**kwargs) -> GovernanceIntent:
    return emit_governance_intent(
        action=GovernanceAction.APPROVE_FOR_PAPER,
        **kwargs,
    )


def propose_reject_for_paper(**kwargs) -> GovernanceIntent:
    return emit_governance_intent(
        action=GovernanceAction.REJECT_FOR_PAPER,
        **kwargs,
    )


def propose_approve_for_live(**kwargs) -> GovernanceIntent:
    return emit_governance_intent(
        action=GovernanceAction.APPROVE_FOR_LIVE,
        **kwargs,
    )


def propose_reject_for_live(**kwargs) -> GovernanceIntent:
    return emit_governance_intent(
        action=GovernanceAction.REJECT_FOR_LIVE,
        **kwargs,
    )
