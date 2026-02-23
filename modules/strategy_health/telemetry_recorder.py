from typing import Optional

from modules.strategy_health.telemetry import (
    StrategyTelemetry,
    HealthSnapshot,
    DecaySnapshot,
    StateSnapshot,
)
from modules.strategy_health.evaluator import HealthResult
from modules.strategy_health.decay_detector import DecaySignal
from modules.strategy_health.state_machine import StateTransition, StrategyState


# ==========================================================
# TELEMETRY RECORDER
# ==========================================================

class TelemetryRecorder:
    """
    Read-only observability recorder.

    Guarantees:
    - Append-only
    - Deterministic step counter
    - No control-path influence
    - Safe for replay & forensics
    """

    def __init__(self, strategy_id: str):
        self._telemetry = StrategyTelemetry(strategy_id=strategy_id)
        self._step = 0

    # ------------------------------------------------------
    # RECORDERS
    # ------------------------------------------------------

    def record_health(self, result: HealthResult) -> None:
        self._telemetry.health.append(
            HealthSnapshot(
                step=self._step,
                health_score=result.health_score,
                signals=dict(result.signals),
                flags=list(result.flags),
            )
        )

    def record_decay(self, signal: DecaySignal) -> None:
        self._telemetry.decay.append(
            DecaySnapshot(
                step=self._step,
                level=signal.level,
                reasons=list(signal.reasons),
                windows_confirmed=list(signal.windows_confirmed),
            )
        )

    def record_state(
        self,
        *,
        current_state: StrategyState,
        transition: Optional[StateTransition],
    ) -> None:
        if transition:
            self._telemetry.state.append(
                StateSnapshot(
                    step=self._step,
                    state=transition.to_state.value,
                    reason=transition.reason,
                )
            )
        else:
            self._telemetry.state.append(
                StateSnapshot(
                    step=self._step,
                    state=current_state.value,
                    reason=None,
                )
            )

    # ------------------------------------------------------
    # STEP CONTROL
    # ------------------------------------------------------

    def next_step(self) -> None:
        self._step += 1

    # ------------------------------------------------------
    # READ-ONLY ACCESS
    # ------------------------------------------------------

    @property
    def telemetry(self) -> StrategyTelemetry:
        return self._telemetry

    @property
    def current_step(self) -> int:
        return self._step
