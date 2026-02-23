from typing import List

from .decision import RollbackDecision
from .audit import RollbackAuditEvent
from .errors import RollbackGovernorError


class RollbackGovernor:
    """
    Observes live metrics and enforces capital rollback.
    Governors:
    - NEVER promote
    - ONLY reduce capital
    - Are monotonic (capital cannot increase)
    """

    def __init__(
        self,
        *,
        rules: List,
        decay_policy,
        allocator,
        audit_sink,
        clock,
    ):
        self.rules = rules
        self.decay_policy = decay_policy
        self.allocator = allocator
        self.audit_sink = audit_sink
        self.clock = clock

    def evaluate(self, *, model_id: str, metrics) -> RollbackDecision:
        reasons: List[str] = []

        for rule in self.rules:
            if rule.evaluate(metrics):
                reasons.append(rule.__class__.__name__)

        if not reasons:
            return RollbackDecision(triggered=False, reasons=[])

        allocation = self.allocator.get(model_id)
        old_weight = allocation.weight
        new_weight = self.decay_policy.next_weight(old_weight)

        if new_weight > old_weight:
            raise RollbackGovernorError("Governor cannot increase capital")

        # Apply decay directly (governors bypass ladder by design)
        allocation.weight = new_weight

        self.audit_sink.emit(
            RollbackAuditEvent(
                model_id=model_id,
                old_weight=old_weight,
                new_weight=new_weight,
                reasons=reasons,
                timestamp=self.clock.utcnow(),
            )
        )

        return RollbackDecision(triggered=True, reasons=reasons)
