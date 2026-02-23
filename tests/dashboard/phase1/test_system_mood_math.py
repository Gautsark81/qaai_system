from dashboard.domain.system_mood import compute_system_mood


class DummySnapshot:
    def __init__(
        self,
        violations=0,
        telemetry=1.0,
        determinism=1.0,
        execution_possible=False,
        capital=0.0,
    ):
        self.violations = {"count": violations}
        self.telemetry = {"completeness": telemetry}
        self.determinism = {"replay_match_rate": determinism}
        self.safety = {
            "execution_possible": execution_possible,
            "capital_allocated": capital,
        }


def test_perfect_system_has_full_mood():
    snap = DummySnapshot()
    result = compute_system_mood(snap)
    assert result.mood == 100


def test_violations_reduce_mood_aggressively():
    snap = DummySnapshot(violations=2)
    result = compute_system_mood(snap)
    assert result.mood <= 60


def test_telemetry_loss_penalized():
    snap = DummySnapshot(telemetry=0.5)
    result = compute_system_mood(snap)
    assert result.penalties.telemetry > 0


def test_nondeterminism_penalized():
    snap = DummySnapshot(determinism=0.8)
    result = compute_system_mood(snap)
    assert result.penalties.determinism > 0


def test_execution_possible_hard_gates_mood():
    snap = DummySnapshot(execution_possible=True)
    result = compute_system_mood(snap)
    assert result.mood == 0
    assert result.hard_gates["execution_possible"] is True


def test_capital_in_shadow_is_penalized():
    snap = DummySnapshot(capital=10.0)
    result = compute_system_mood(snap)
    assert result.mood < 100
