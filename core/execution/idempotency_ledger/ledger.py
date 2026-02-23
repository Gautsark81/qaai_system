# core/execution/idempotency_ledger/ledger.py

from typing import Iterable, List, Dict

from core.execution.idempotency_ledger.models import ExecutionIdempotencyRecord
from core.execution.idempotency_ledger.result import (
    IdempotencyDecision,
    IdempotencyResult,
)


class ExecutionIdempotencyLedger:
    """
    Append-only, deterministic idempotency ledger.

    - No execution authority
    - No mutation
    - Restart-safe via replay
    """

    def __init__(self) -> None:
        self._records: List[ExecutionIdempotencyRecord] = []
        self._seen_hashes: Dict[str, ExecutionIdempotencyRecord] = {}

    def record(
        self,
        record: ExecutionIdempotencyRecord,
        *,
        replay: bool = False,
    ) -> IdempotencyResult:
        identity = record.identity_hash()

        if identity in self._seen_hashes:
            return IdempotencyResult(
                decision=(
                    IdempotencyDecision.REPLAYED
                    if replay
                    else IdempotencyDecision.DUPLICATE
                ),
                identity_hash=identity,
            )

        self._records.append(record)
        self._seen_hashes[identity] = record

        return IdempotencyResult(
            decision=(
                IdempotencyDecision.REPLAYED
                if replay
                else IdempotencyDecision.ACCEPTED
            ),
            identity_hash=identity,
        )

    def entries(self) -> List[ExecutionIdempotencyRecord]:
        return list(self._records)

    @classmethod
    def replay(
        cls,
        records: Iterable[ExecutionIdempotencyRecord],
    ) -> "ExecutionIdempotencyLedger":
        ledger = cls()
        for record in records:
            ledger.record(record, replay=True)
        return ledger
