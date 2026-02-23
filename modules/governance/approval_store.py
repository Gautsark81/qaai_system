from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from modules.governance.approval import ApprovalRecord, ApprovalDecision


class ApprovalStore:
    """
    Persistent store abstraction.
    Backed by DB / KV / file adapter later.
    """

    def __init__(self):
        self._store: Dict[str, ApprovalRecord] = {}

    def save(self, record: ApprovalRecord):
        self._store[record.strategy_id] = record

    def get(self, strategy_id: str) -> Optional[ApprovalRecord]:
        return self._store.get(strategy_id)

    def is_approved(self, strategy_id: str, now: datetime) -> bool:
        record = self.get(strategy_id)
        if not record:
            return False

        if record.decision != ApprovalDecision.APPROVED:
            return False

        if record.expires_at and record.expires_at < now:
            return False

        return True
