# core/evidence/tests/test_governance_signature.py

from datetime import datetime, timezone

from core.evidence.governance_binder import bind_governance_signature
from core.evidence.signing import verify_signature


def test_governance_signature_roundtrip():
    secret = b"test-secret"

    signed = bind_governance_signature(
        decision_id="dec-001",
        governance_type="PAPER",
        strategy_id="alpha_1",
        status="APPROVED",
        reasons=["SSR above threshold"],
        reviewer="risk_officer",
        reviewer_fingerprint="user-123",
        decided_at=datetime.now(timezone.utc),
        decision_checksum="chk-abc",
        secret=secret,
    )

    payload = "|".join([
        signed.decision_id,
        signed.governance_type,
        signed.strategy_id,
        signed.status,
        signed.reviewer,
        signed.decision_checksum,
    ])

    assert verify_signature(
        payload=payload,
        signature=signed.signature,
        secret=secret,
    )
