from datetime import datetime
from typing import List

from core.execution.replay.engine import ReplayEngine
from core.execution.replay.envelope import ReplayEnvelope
from core.execution.replay.results import ReplayEvent, ReplayResult
from core.execution.telemetry import ExecutionEvent, ExecutionTelemetry
from core.execution.invariant_validator import validate_execution_invariants


class DeterministicReplayEngine(ReplayEngine):
    """
    Deterministic, side-effect-free replay engine.
    """

    def run(self, envelope: ReplayEnvelope) -> ReplayResult:
        try:
            telemetry = self._reconstruct_telemetry(envelope)
            invariant_result = validate_execution_invariants(telemetry)

            replay_events = tuple(
                ReplayEvent(
                    timestamp=e.timestamp,
                    event_type=e.event_type,
                    message=e.message,
                )
                for e in telemetry.events
            )

            return ReplayResult(
                replay_id=envelope.identity.replay_id,
                execution_id=envelope.identity.execution_id,
                completed_at=datetime.utcnow(),
                reconstructed_events=replay_events,
                invariant_violations=tuple(
                    v.code for v in invariant_result.violations
                ),
            )

        except Exception as exc:
            # Replay must never raise
            return ReplayResult(
                replay_id=envelope.identity.replay_id,
                execution_id=envelope.identity.execution_id,
                completed_at=datetime.utcnow(),
                reconstructed_events=(),
                invariant_violations=(f"REPLAY_ERROR:{type(exc).__name__}",),
            )

    # --------------------------------------------------

    def _reconstruct_telemetry(
        self, envelope: ReplayEnvelope
    ) -> ExecutionTelemetry:
        """
        Deterministically reconstruct ExecutionTelemetry
        from persisted telemetry records.
        """

        records = envelope.inputs.telemetry_records

        # Rebuild ExecutionEvent list
        events: List[ExecutionEvent] = []
        for r in records:
            events.append(
                ExecutionEvent(
                    timestamp=self._parse_dt(r["timestamp"]),
                    event_type=r["event_type"],
                    message=r["message"],
                )
            )

        # NOTE: counts are reconstructed deterministically
        return ExecutionTelemetry(
            execution_id=envelope.identity.execution_id,
            started_at=self._parse_dt(envelope.inputs.environment["started_at"]),
            completed_at=None,
            total_orders=envelope.inputs.config_snapshot["total_orders"],
            filled_orders=envelope.inputs.config_snapshot["filled_orders"],
            rejected_orders=envelope.inputs.config_snapshot["rejected_orders"],
            cancelled_orders=envelope.inputs.config_snapshot["cancelled_orders"],
            events=tuple(events),
        )

    @staticmethod
    def _parse_dt(value):
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)
