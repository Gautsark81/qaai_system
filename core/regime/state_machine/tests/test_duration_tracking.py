from core.regime.state_machine.duration_tracker import compute_duration_and_age


def test_duration_increments():
    duration, age = compute_duration_and_age("BULL", 5, "BULL")
    assert duration == 6
    assert age == "mid"


def test_duration_resets_on_label_change():
    duration, age = compute_duration_and_age("BULL", 5, "BEAR")
    assert duration == 1
    assert age == "early"