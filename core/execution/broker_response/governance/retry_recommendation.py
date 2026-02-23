from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime

from core.execution.broker_response.governance.outcome import BrokerOutcome
from core.execution.broker_response.governance.retry_decision import RetryDecision


@dataclass(frozen=True)
class RetryRecommendation:
    """
    Canonical retry recommendation (governance-only).

    No execution authority.
    Deterministic.
    Replay-safe.
    """

    outcome: BrokerOutcome
    retry_decision: RetryDecision
    response_hash: str
    reason: str
    timestamp: datetime

    @property
    def recommendation_hash(self) -> str:
        payload = json.dumps(
            asdict(self),
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return hashlib.sha256(payload.encode()).hexdigest()


__all__ = ["RetryRecommendation"]
