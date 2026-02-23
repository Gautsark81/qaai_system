# core/governance/integrity/governance_snapshot_serializer.py

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict

from core.governance.reconstruction import GovernanceState


class GovernanceSnapshotSerializer:
    """
    Phase C6.1

    Canonical serializer for GovernanceState.

    Guarantees:
    - Deterministic ordering
    - Stable float formatting
    - ISO-8601 UTC timestamps
    - No mutation of input
    - No side effects
    """

    @staticmethod
    def serialize(state: GovernanceState) -> str:
        data = GovernanceSnapshotSerializer._normalize(asdict(state))
        return json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @staticmethod
    def _normalize(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: GovernanceSnapshotSerializer._normalize(value[key])
                for key in sorted(value.keys())
            }

        if isinstance(value, list):
            return [GovernanceSnapshotSerializer._normalize(v) for v in value]

        if isinstance(value, float):
            # stable float normalization
            return float(f"{value:.10f}".rstrip("0").rstrip("."))

        if isinstance(value, datetime):
            return (
                value.astimezone(timezone.utc)
                .replace(tzinfo=timezone.utc)
                .isoformat()
            )

        return value