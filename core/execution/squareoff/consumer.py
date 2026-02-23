from __future__ import annotations

from typing import Dict, Optional, List

from core.execution.squareoff.intent import SquareOffIntent
from core.execution.squareoff.execution_intent import SquareOffExecutionIntent
from core.evidence.models import AuditEvidence


class SquareOffConsumer:
    """
    Consumes positions under a forced square-off intent.
    """

    def __init__(
        self,
        *,
        positions: Dict[str, int],
        squareoff_intent: SquareOffIntent,
        strategy: Optional[object] = None,
    ):
        self._positions = positions
        self._intent = squareoff_intent
        self._strategy = strategy

        self._consumed = False
        self._evidence: Optional[AuditEvidence] = None
        self._exec_intents: List[SquareOffExecutionIntent] = []

    # -------------------------------------------------
    # SAFETY GATE
    # -------------------------------------------------
    def assert_normal_execution_allowed(self) -> None:
        raise RuntimeError(
            f"Normal execution blocked due to forced square-off: {self._intent.reason}"
        )

    # -------------------------------------------------
    # CONSUMPTION
    # -------------------------------------------------
    def consume(self) -> List[SquareOffExecutionIntent]:
        if self._consumed:
            return self._exec_intents

        # HARD RULE: strategy must never be touched

        self._evidence = AuditEvidence(
            audit_id=self._intent.audit_id,
            reason=self._intent.reason,
            positions=dict(self._positions),
        )

        for symbol, qty in self._positions.items():
            if qty == 0:
                continue

            self._exec_intents.append(
                SquareOffExecutionIntent(
                    symbol=symbol,
                    qty=-qty,
                    reason=self._intent.reason,
                    audit_id=self._intent.audit_id,
                )
            )


        self._consumed = True
        return self._exec_intents

    # -------------------------------------------------
    # AUDIT
    # -------------------------------------------------
    @property
    def evidence(self) -> AuditEvidence:
        if not self._evidence:
            raise RuntimeError("Square-off not yet consumed")
        return self._evidence
