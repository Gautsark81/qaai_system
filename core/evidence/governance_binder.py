# core/evidence/governance_binder.py

from datetime import timezone
from core.evidence.governance_contracts import SignedGovernanceEvidence
from core.evidence.signing import sign_payload


def bind_governance_signature(
    *,
    decision_id: str,
    governance_type: str,
    strategy_id: str,
    status: str,
    reasons: list[str],
    reviewer: str,
    reviewer_fingerprint: str,
    decided_at,
    decision_checksum: str,
    secret: bytes,
) -> SignedGovernanceEvidence:
    """
    Bind a governance decision to a cryptographic signature.

    This function is PURE.
    """

    payload = "|".join([
        decision_id,
        governance_type,
        strategy_id,
        status,
        reviewer,
        decision_checksum,
    ])

    signature = sign_payload(
        payload=payload,
        secret=secret,
    )

    return SignedGovernanceEvidence(
        decision_id=decision_id,
        governance_type=governance_type,
        strategy_id=strategy_id,
        status=status,
        reasons=tuple(reasons),
        reviewer=reviewer,
        reviewer_fingerprint=reviewer_fingerprint,
        decided_at=decided_at.astimezone(timezone.utc),
        decision_checksum=decision_checksum,
        signature=signature,
        algorithm="HMAC-SHA256",
    )
