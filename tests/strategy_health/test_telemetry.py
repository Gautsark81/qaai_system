from modules.strategy_health.telemetry_recorder import TelemetryRecorder
from modules.strategy_health.evaluator import HealthResult
from modules.strategy_health.decay_detector import DecaySignal
from modules.strategy_health.state_machine import StrategyState, StateTransition


def _health(step, score):
    return HealthResult(
        strategy_id="s1",
        health_score=score,
        signals={"win_rate": 1.0, "drawdown": 1.0},
        flags=[],
        window=50,
        reason="test",
    )


def test_telemetry_append_only():
    recorder = TelemetryRecorder("s1")

    recorder.record_health(_health(0, 0.9))
    recorder.next_step()
    recorder.record_health(_health(1, 0.8))
    recorder.next_step()

    assert len(recorder.telemetry.health) == 2
    assert recorder.telemetry.health[0].step == 0
    assert recorder.telemetry.health[1].step == 1


def test_state_recording_with_transition():
    recorder = TelemetryRecorder("s1")

    tr = StateTransition(
        from_state=StrategyState.ACTIVE,
        to_state=StrategyState.PAUSED,
        reason="test pause",
    )

    recorder.record_state(
        current_state=StrategyState.ACTIVE,
        transition=tr,
    )

    snap = recorder.telemetry.last_state()
    assert snap.state == "PAUSED"
    assert snap.reason == "test pause"


def test_decay_recording():
    recorder = TelemetryRecorder("s1")

    decay = DecaySignal(
        level="STRUCTURAL_DECAY",
        reasons=["health trend", "drawdown"],
        windows_confirmed=[30, 60],
    )

    recorder.record_decay(decay)

    snap = recorder.telemetry.last_decay()
    assert snap.level == "STRUCTURAL_DECAY"
    assert 60 in snap.windows_confirmed


def test_step_monotonicity():
    recorder = TelemetryRecorder("s1")

    recorder.record_health(_health(0, 0.9))
    recorder.next_step()
    recorder.record_health(_health(1, 0.7))
    recorder.next_step()
    recorder.record_health(_health(2, 0.6))

    steps = [h.step for h in recorder.telemetry.health]
    assert steps == [0, 1, 2]
