# File: tests/dashboard/test_dashboard_schema.py

def test_dashboard_schema_is_stable():
    from core.dashboard.export import export_dashboard_state
    snapshot = export_dashboard_state()

    assert "timestamp" in snapshot
    assert "system_health" in snapshot
    assert "roadmap" in snapshot
    assert isinstance(snapshot["roadmap"], list)
