from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from core.v2.live_bridge.contracts import LiveApprovalRecord


class ApprovalStore:
    """
    Append-only store for live trading approvals.

    Governance rules:
    - Revocation overrides approval immediately
    - Multiple active approvals (non-revoked) are illegal
    """

    def __init__(self):
        self._records: Dict[str, List[LiveApprovalRecord]] = {}

    def add(self, record: LiveApprovalRecord) -> None:
        self._records.setdefault(record.strategy_id, []).append(record)

    def get_active(
        self,
        *,
        strategy_id: str,
        now: datetime,
    ) -> LiveApprovalRecord | None:
        records = self._records.get(strategy_id, [])

        active = [
            r for r in records
            if r.approved_at <= now <= r.expires_at
        ]

        if not active:
            return None

        # 🔴 REVOCATION OVERRIDES EVERYTHING
        revoked = [
            r for r in active
            if r.notes.startswith("REVOKED")
        ]

        if revoked:
            return None

        if len(active) > 1:
            raise RuntimeError(
                f"Multiple active approvals for strategy {strategy_id}"
            )

        return active[0]
