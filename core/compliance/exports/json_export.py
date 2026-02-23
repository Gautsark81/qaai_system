# core/compliance/export/json_export.py

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from core.compliance.exports.contracts import AuditExport, ExportSeal


# ---------------------------------------------------------------------
# JSON Export (Machine-Verifiable)
# ---------------------------------------------------------------------

class JSONAuditExporter:
    """
    Deterministic JSON exporter for sealed audit artifacts.

    Guarantees:
    - No execution authority
    - Replay-safe
    - Hash-verifiable
    """

    @staticmethod
    def export(
        *,
        audit_export: AuditExport,
        seal: ExportSeal,
    ) -> Dict[str, Any]:
        """
        Produce a canonical JSON-serializable dict.

        This function does NOT:
        - write files
        - mutate inputs
        - depend on system state
        """

        return {
            "metadata": asdict(audit_export.metadata),
            "artifacts": audit_export.artifacts,
            "seal": {
                "algorithm": seal.algorithm,
                "digest": seal.digest,
                "canonical_order": list(seal.canonical_order),
            },
        }
