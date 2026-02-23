# core/evidence/report_json.py

import json
from dataclasses import asdict
from typing import Any

from core.evidence.report_contracts import ReplayAuditReport


def _json_default(value: Any) -> str:
    """
    Deterministic fallback serializer.

    Rules:
    - Never mutates objects
    - Always returns stable string representation
    """
    return str(value)


def export_report_json(
    *,
    report: ReplayAuditReport,
    pretty: bool = True,
) -> str:
    """
    Export audit report as canonical JSON.

    Guarantees:
    - Deterministic key ordering
    - No mutation of report
    - Stable serialization across runs
    """

    # dataclasses → pure dict (no mutation)
    data = asdict(report)

    # Canonical JSON output
    if pretty:
        return json.dumps(
            data,
            indent=2,
            sort_keys=True,        # 🔒 determinism
            default=_json_default,
        )

    return json.dumps(
        data,
        sort_keys=True,            # 🔒 determinism
        default=_json_default,
    )
