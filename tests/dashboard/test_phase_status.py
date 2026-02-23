# File: tests/dashboard/test_phase_status.py

ALLOWED = {
    "LOCKED",
    "COMPLETE",
    "IN_PROGRESS",
    "PARTIAL",
    "PENDING",
    "BLOCKED",
}


def test_all_phases_have_valid_status():
    from core.dashboard.roadmap import get_full_roadmap
    for phase in get_full_roadmap():
        assert phase["status"] in ALLOWED
