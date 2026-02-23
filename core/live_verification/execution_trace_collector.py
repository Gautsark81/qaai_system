from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from .models import ExecutionTraceEvidence


class ExecutionTraceCollector:
    """
    Read-only trace collector.
    Does not mutate execution.
    """

    def _hash(self, obj: Any) -> str:
        payload = json.dumps(obj, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()

    def collect(
        self,
        *,
        strategy_dna: str,
        capital_decision: Any,
        risk_verdict: Any,
        execution_intent: Any,
        router_call_payload: Any,
        mode: str,
    ) -> ExecutionTraceEvidence:

        return ExecutionTraceEvidence(
            strategy_dna=strategy_dna,
            capital_decision_hash=self._hash(capital_decision),
            risk_verdict_hash=self._hash(risk_verdict),
            execution_intent_hash=self._hash(execution_intent),
            router_call_hash=self._hash(router_call_payload),
            mode=mode,
            timestamp_utc=datetime.utcnow().isoformat(),
        )