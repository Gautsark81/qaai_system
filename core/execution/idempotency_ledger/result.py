# core/execution/idempotency_ledger/result.py

from dataclasses import dataclass
from enum import Enum


class IdempotencyDecision(str, Enum):
    ACCEPTED = "ACCEPTED"
    DUPLICATE = "DUPLICATE"
    REPLAYED = "REPLAYED"


@dataclass(frozen=True)
class IdempotencyResult:
    decision: IdempotencyDecision
    identity_hash: str
