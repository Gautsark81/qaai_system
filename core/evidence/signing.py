# core/evidence/signing.py

import hmac
import hashlib


def sign_payload(
    *,
    payload: str,
    secret: bytes,
    algorithm: str = "sha256",
) -> str:
    """
    Deterministic HMAC signature.

    - Pure
    - No IO
    - No globals
    """

    h = hmac.new(secret, payload.encode("utf-8"), getattr(hashlib, algorithm))
    return h.hexdigest()


def verify_signature(
    *,
    payload: str,
    signature: str,
    secret: bytes,
    algorithm: str = "sha256",
) -> bool:
    expected = sign_payload(
        payload=payload,
        secret=secret,
        algorithm=algorithm,
    )
    return hmac.compare_digest(expected, signature)
