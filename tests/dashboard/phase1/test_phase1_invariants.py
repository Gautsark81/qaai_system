import pytest
from datetime import datetime
from dashboard.domain.phase1_state import Phase1SystemState
from dashboard.domain.invariants import Phase1InvariantViolation, assert_phase1_invariants

def base_state():
    return Phase1SystemState(
        run_id="test",
        mode="paper",
        boot_timestamp=datetime.utcnow(),
        last_heartbeat_ts=None,
        uptime_sec=0,
        execution_possible=False,
        capital_allocated=0.0,
        kill_switch_state="armed",
        intent_count=0,
        determinism_hashes=[],
        replay_match_rate=1.0,
        telemetry_expected=0,
        telemetry_written=0,
        telemetry_completeness=1.0,
        violation_count=0,
        violation_rate=0.0,
        last_violation_ts=None,
        system_mood_index=100.0,
        violation_pulse=0.0,
    )

def test_execution_must_never_be_possible():
    s = base_state().__class__(**{**base_state().__dict__, "execution_possible": True})
    with pytest.raises(Phase1InvariantViolation):
        assert_phase1_invariants(s)
