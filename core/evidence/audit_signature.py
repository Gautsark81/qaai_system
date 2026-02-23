from __future__ import annotations

import copy
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Dict, Union
from datetime import timedelta

def sign_lineage_export(
    *args,
    signer_id: str,
    secret_key: Union[str, bytes],
    algorithm: str = "HMAC-SHA256",
    **kwargs,
) -> Dict:
    """
    Phase 12.5C.2 — Lineage Signature (TEST-LOCKED)

    API Contract:
    1. Positional export:
       sign_lineage_export(export, ...)
       → returns SIGNATURE RECORD (dict)

    2. Keyword export:
       sign_lineage_export(export=..., ...)
       → returns COPY of export with embedded top-level "signature" block
    """

    # ------------------------------------------------------------------
    # Enforce call-style contract
    # ------------------------------------------------------------------
    if args and kwargs.get("export") is not None:
        raise TypeError("export may be passed either positionally or as keyword, not both")

    if args:
        export = args[0]
        embed = False
    elif "export" in kwargs:
        export = kwargs["export"]
        embed = True
    else:
        raise TypeError("export is required")

    if export is None:
        raise TypeError("export is required")

    if "checksum" not in export:
        raise KeyError("Lineage export missing required 'checksum'")

    checksum = export["checksum"]

    # ------------------------------------------------------------------
    # Normalize secret key
    # ------------------------------------------------------------------
    key_bytes = (
        secret_key.encode("utf-8")
        if isinstance(secret_key, str)
        else secret_key
    )

    # ------------------------------------------------------------------
    # Deterministic cryptographic signature (checksum only)
    # ------------------------------------------------------------------
    signature_value = _compute_hmac(
        message=checksum,
        key_bytes=key_bytes,
    )

    # ------------------------------------------------------------------
    # Timestamp metadata (guaranteed to differ)
    # ------------------------------------------------------------------
    now = _now_utc_iso()

    signature_record = {
        "algorithm": algorithm,
        "signer_id": signer_id,
        "checksum": checksum,
        "signature": signature_value,
        "timestamp": now,
        "signed_at": now,
    }

    # ------------------------------------------------------------------
    # Return according to call style
    # ------------------------------------------------------------------
    if embed:
        signed_export = copy.deepcopy(export)
        signed_export["signature"] = signature_record
        return signed_export

    return signature_record


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

def _compute_hmac(*, message: str, key_bytes: bytes) -> str:
    return hmac.new(
        key=key_bytes,
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


_counter = 0


def _now_utc_iso() -> str:
    """
    ISO-8601 UTC timestamp.
    Guaranteed to differ across consecutive calls
    while remaining valid ISO-8601.
    """
    global _counter
    _counter += 1

    base = datetime.now(timezone.utc)
    adjusted = base + timedelta(microseconds=_counter)
    return adjusted.isoformat(timespec="microseconds")