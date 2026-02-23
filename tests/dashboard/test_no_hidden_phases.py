# File: tests/dashboard/test_no_hidden_phases.py

def test_no_phase_is_hidden_from_dashboard():
    from core.dashboard.roadmap import get_full_roadmap
    for phase in get_full_roadmap():
        assert phase.get("visible", True) is True
