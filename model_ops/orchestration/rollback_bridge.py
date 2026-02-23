from datetime import timedelta
from typing import Dict

from qaai_system.model_ops.decay_detection import DecayDecision
from qaai_system.model_ops.orchestration.state import BridgeState
from qaai_system.model_ops.orchestration.audit import RollbackBridgeAuditEvent


class DecayRollbackBridge:
    """
    Bridges E4 decay signals to E3.5 rollback governors.

    Guarantees:
    - At most one rollback per cooldown window
    - No action if no decay
    - Fully auditable
    """

    def __init__(
        self,
        *,
        governor,
        audit_sink,
        clock,
        cooldown: timedelta,
    ):
        self.governor = governor
        self.audit_sink = audit_sink
        self.clock = clock
        self.cooldown = cooldown
        self._state: Dict[str, BridgeState] = {}

    def on_decay(
        self,
        *,
        model_id: str,
        decay_decision: DecayDecision,
        metrics,
    ) -> None:
        now = self.clock.utcnow()

        state = self._state.setdefault(model_id, BridgeState())

        # No decay → no action
        if not decay_decision.decaying:
            self.audit_sink.emit(
                RollbackBridgeAuditEvent(
                    model_id=model_id,
                    decay_reasons=[],
                    triggered=False,
                    timestamp=now,
                )
            )
            return

        # Cooldown enforcement
        if (
            state.last_triggered_at is not None
            and now - state.last_triggered_at < self.cooldown
        ):
            self.audit_sink.emit(
                RollbackBridgeAuditEvent(
                    model_id=model_id,
                    decay_reasons=decay_decision.reasons,
                    triggered=False,
                    timestamp=now,
                )
            )
            return

        # Trigger rollback governor
        self.governor.evaluate(
            model_id=model_id,
            metrics=metrics,
        )

        state.last_triggered_at = now

        self.audit_sink.emit(
            RollbackBridgeAuditEvent(
                model_id=model_id,
                decay_reasons=decay_decision.reasons,
                triggered=True,
                timestamp=now,
            )
        )
