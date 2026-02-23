# core/compliance/exports/exporter.py
import json
import hashlib
from typing import List, Dict, Any

from core.compliance.exports.models import SEBIAuditExport


class SEBIAuditExporter:
    """
    Builds SEBI-grade deterministic audit exports.
    """

    def build(
        self,
        *,
        trades: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
        explanations: List[str],
    ) -> SEBIAuditExport:
        # Deterministic ordering
        trades_sorted = sorted(trades, key=lambda t: json.dumps(t, sort_keys=True))
        decisions_sorted = sorted(decisions, key=lambda d: json.dumps(d, sort_keys=True))
        explanations_sorted = sorted(explanations)

        payload = {
            "trades": trades_sorted,
            "decisions": decisions_sorted,
            "explanations": explanations_sorted,
        }

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        export_id = hashlib.sha256(canonical).hexdigest()

        return SEBIAuditExport(
            export_id=export_id,
            trades=trades_sorted,
            decisions=decisions_sorted,
            explanations=explanations_sorted,
        )
