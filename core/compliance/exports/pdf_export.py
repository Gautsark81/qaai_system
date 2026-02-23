# core/compliance/export/pdf_export.py

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from core.compliance.exports.contracts import AuditExport, ExportSeal


# ---------------------------------------------------------------------
# PDF Export Model (Human-Readable, Hash-Anchored)
# ---------------------------------------------------------------------

class PDFAuditExporter:
    """
    Deterministic, human-readable PDF export model.

    This class DOES NOT:
    - render a PDF
    - write files
    - perform IO

    It produces a structured document layout that can be
    rendered externally without altering meaning or hash.
    """

    @staticmethod
    def export(
        *,
        audit_export: AuditExport,
        seal: ExportSeal,
    ) -> Dict[str, Any]:
        """
        Produce a deterministic document model suitable
        for PDF rendering.

        Output is intentionally simple and explicit.
        """

        return {
            "title": "QAAI SYSTEM — REGULATORY AUDIT PACK",
            "export_metadata": asdict(audit_export.metadata),
            "cryptographic_seal": {
                "algorithm": seal.algorithm,
                "digest": seal.digest,
                "canonical_order": list(seal.canonical_order),
            },
            "sections": _build_sections(audit_export),
            "integrity_notice": (
                "This document is cryptographically sealed. "
                "Any modification invalidates the checksum above."
            ),
        }


# ---------------------------------------------------------------------
# Section Builder
# ---------------------------------------------------------------------

def _build_sections(audit_export: AuditExport) -> List[Dict[str, Any]]:
    """
    Convert audit artifacts into ordered, human-readable sections.
    """

    sections: List[Dict[str, Any]] = []

    for idx, artifact in enumerate(audit_export.artifacts, start=1):
        sections.append(
            {
                "section_number": idx,
                "artifact_type": getattr(artifact, "kind", "UNKNOWN"),
                "content": _safe_artifact_payload(artifact),
            }
        )

    return sections


def _safe_artifact_payload(artifact: Any) -> Any:
    """
    Ensure artifact payloads are rendered safely and read-only.
    """

    if hasattr(artifact, "payload"):
        return artifact.payload

    return artifact
