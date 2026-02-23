from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass(frozen=True)
class GovernanceDecision:
    strategy_id: str
    decision: str
    actor: str
    timestamp: datetime
    reason: str


class GovernanceDecisionLog:
    def __init__(self):
        self._events: List[GovernanceDecision] = []

    def record(self, event: GovernanceDecision):
        self._events.append(event)

    def all(self) -> List[GovernanceDecision]:
        return list(self._events)
