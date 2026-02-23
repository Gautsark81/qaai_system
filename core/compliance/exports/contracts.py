# core/compliance/export/contracts.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, runtime_checkable


# ---------------------------------------------------------------------
# Core Export Contracts
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ExportMetadata:
    """
    Metadata attached to every regulator export.

    Rules:
    - Must be deterministic
    - Must not contain secrets
    - Must not grant authority
    """

    export_version: str
    export_type: str
    generated_by: str
    generated_at_iso: str  # injected timestamp (not system time)


@dataclass(frozen=True)
class AuditExport:
    """
    Immutable export payload delivered to regulators.

    This is the canonical object that is hashed, sealed,
    serialized, and verified.
    """

    metadata: ExportMetadata
    artifacts: List[Any]  # AuditPack artifacts + narratives
    checksum: str         # cryptographic seal (SHA-256)


# ---------------------------------------------------------------------
# Cryptographic Seal Contracts
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ExportSeal:
    """
    Cryptographic seal attached to an export.

    Guarantees:
    - Tamper detection
    - Deterministic recomputation
    """

    algorithm: str        # e.g. "SHA256"
    digest: str           # hex digest
    canonical_order: List[str]  # fields included in hash


# ---------------------------------------------------------------------
# Verifier Interfaces (NO IMPLEMENTATION HERE)
# ---------------------------------------------------------------------

@runtime_checkable
class ExportHasher(Protocol):
    """
    Canonical hashing interface.

    Implementations must:
    - Be deterministic
    - Use canonical ordering
    - Never access system state
    """

    def hash(self, payload: Dict[str, Any]) -> str:
        ...


@runtime_checkable
class ExportVerifier(Protocol):
    """
    Verification interface for sealed exports.
    """

    def verify(self, export: AuditExport) -> bool:
        ...


# ---------------------------------------------------------------------
# Safety Contracts
# ---------------------------------------------------------------------

@runtime_checkable
class NoExecutionAuthority(Protocol):
    """
    Marker protocol.

    Any export component implementing execution,
    mutation, or side effects MUST NOT satisfy this.
    """
    pass
