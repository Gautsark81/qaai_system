# core/compliance/export/seal.py

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from core.compliance.exports.contracts import (
    AuditExport,
    ExportSeal,
    ExportHasher,
)


# ---------------------------------------------------------------------
# Canonical Payload Builder
# ---------------------------------------------------------------------

def _build_canonical_payload(export: AuditExport) -> Dict[str, Any]:
    """
    Construct the canonical payload used for hashing.

    Rules:
    - Only include fields explicitly allowed
    - Never include checksum itself
    - Preserve semantic meaning, not object identity
    """

    return {
        "metadata": asdict(export.metadata),
        "artifacts": export.artifacts,
    }


# ---------------------------------------------------------------------
# Seal Builder
# ---------------------------------------------------------------------

def seal_export(
    *,
    export: AuditExport,
    hasher: ExportHasher,
) -> ExportSeal:
    """
    Compute a cryptographic seal for an AuditExport.

    This function is PURE:
    - No mutation
    - No side effects
    """

    payload = _build_canonical_payload(export)

    digest = hasher.hash(payload)

    return ExportSeal(
        algorithm=hasher.algorithm,
        digest=digest,
        canonical_order=["metadata", "artifacts"],
    )


# ---------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------

def verify_export(
    *,
    export: AuditExport,
    hasher: ExportHasher,
) -> bool:
    """
    Verify that an AuditExport has not been tampered with.

    Returns:
    - True if checksum matches recomputed hash
    - False otherwise
    """

    payload = _build_canonical_payload(export)
    expected = hasher.hash(payload)

    return export.checksum == expected
