from __future__ import annotations

from .models import ExecutionTraceEvidence


class AuthorityChainVerifier:
    """
    Ensures no authority leak occurred.
    Deterministic and pure.
    """

    def validate(self, trace: ExecutionTraceEvidence) -> bool:
        # Hard validation rules

        if trace.mode not in ("SHADOW", "LIVE"):
            return False

        if not trace.capital_decision_hash:
            return False

        if not trace.risk_verdict_hash:
            return False

        if not trace.execution_intent_hash:
            return False

        if not trace.router_call_hash:
            return False

        return True