from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional
import hashlib


@dataclass(frozen=True)
class GovernanceStrikeEntry:
    governance_id: str
    strategy_id: str
    reason: str
    decision_checksum: str
    strike_number: int
    previous_hash: Optional[str]
    entry_hash: str
    timestamp: datetime

    # Required by tests
    def compute_hash(self) -> str:
        payload = (
            f"{self.governance_id}|{self.strategy_id}|{self.reason}|"
            f"{self.decision_checksum}|{self.strike_number}|"
            f"{self.previous_hash}|{self.timestamp.isoformat()}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()


class GovernanceStrikeLedger:

    def __init__(self):
        self._entries: List[GovernanceStrikeEntry] = []

    @property
    def entries(self) -> List[GovernanceStrikeEntry]:
        return list(self._entries)

    # ---- Core Append ----
    def append_strike(
        self,
        *,
        governance_id: str,
        strategy_id: str,
        reason: str,
        decision_checksum: str,
        timestamp: Optional[datetime] = None,
    ) -> GovernanceStrikeEntry:

        ts = timestamp or datetime.now(timezone.utc)

        existing = [
            e for e in self._entries if e.governance_id == governance_id
        ]

        strike_number = len(existing) + 1
        previous_hash = existing[-1].entry_hash if existing else None

        payload = (
            f"{governance_id}|{strategy_id}|{reason}|"
            f"{decision_checksum}|{strike_number}|"
            f"{previous_hash}|{ts.isoformat()}"
        )

        entry_hash = hashlib.sha256(payload.encode()).hexdigest()

        entry = GovernanceStrikeEntry(
            governance_id=governance_id,
            strategy_id=strategy_id,
            reason=reason,
            decision_checksum=decision_checksum,
            strike_number=strike_number,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
            timestamp=ts,
        )

        self._entries.append(entry)
        return entry

    # ---- Compatibility Layer ----
    def add_strike(self, governance_id: str, reason: str) -> GovernanceStrikeEntry:
        # Used by breach sentinel tests
        return self.append_strike(
            governance_id=governance_id,
            strategy_id="UNKNOWN",
            reason=reason,
            decision_checksum="AUTO",
        )

    def get_strike_count(self, governance_id: str) -> int:
        return len([e for e in self._entries if e.governance_id == governance_id])

    def get_last_strike(self, governance_id: str) -> Optional[GovernanceStrikeEntry]:
        relevant = [
            e for e in self._entries if e.governance_id == governance_id
        ]
        if not relevant:
            return None
        return sorted(relevant, key=lambda x: x.timestamp)[-1]