# core/explainability/decision_trace.py

from datetime import datetime
from typing import Dict, Any, Optional

from core.strategy_factory.registry import StrategyRegistry


class DecisionTraceExplainer:
    """
    Explains WHY a governance / execution decision occurred.

    Sources:
    - Lifecycle transitions
    - Canary audit logs
    - Capital / risk audit events

    Read-only, deterministic.
    """

    def __init__(
        self,
        *,
        registry: StrategyRegistry,
        audit_log: Optional[object] = None,
    ):
        """
        audit_log:
            Optional audit store exposing .all() → list[events]
        """
        self.registry = registry
        self.audit_log = audit_log

    def explain(self, dna: str) -> Dict[str, Any]:
        record = self.registry.get(dna)

        lifecycle_reason = self._explain_lifecycle(record)
        audit_reason = self._explain_audit(dna)

        return {
            "strategy_id": dna,
            "current_state": record.state,
            "decision_trace": {
                "lifecycle": lifecycle_reason,
                "audit": audit_reason,
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

    # -------------------------
    # Internals
    # -------------------------

    @staticmethod
    def _explain_lifecycle(record) -> Dict[str, Any]:
        history = getattr(record, "history", [])

        if not history:
            return {
                "type": "NONE",
                "explanation": "No lifecycle transitions recorded.",
            }

        last = history[-1]

        return {
            "type": "LIFECYCLE",
            "from": last["from"],
            "to": last["to"],
            "explanation": f"Strategy transitioned from {last['from']} to {last['to']}.",
        }

    def _explain_audit(self, dna: str):
        if not self.audit_log:
            return {
                "type": "NONE",
                "explanation": "No audit source attached.",
            }

        events = [e for e in self.audit_log.all() if e.dna == dna]

        if not events:
            return {
                "type": "NONE",
                "explanation": "No audit events recorded.",
            }

        last = events[-1]

        explanation_map = {
            "CANARY_FREEZE": "Strategy execution frozen due to canary risk breach.",
            "CANARY_DOWNGRADE": "Strategy downgraded due to severe canary divergence.",
            "CAPITAL_GUARD_BLOCK": "Order blocked by capital governance limits.",
        }

        return {
            "type": "AUDIT",
            "event_type": last.event_type,
            "explanation": explanation_map.get(
                last.event_type,
                f"Audit event {last.event_type} recorded.",
            ),
        }
