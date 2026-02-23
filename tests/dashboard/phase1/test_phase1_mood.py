from dashboard.domain.aggregates import compute_system_mood

def test_system_mood_degrades_with_violations():
    class Dummy:
        violation_rate = 5
        telemetry_completeness = 1.0
        execution_possible = False

    mood = compute_system_mood(Dummy())
    assert mood < 70
