from core.dashboard_read.providers.compliance import build_compliance_state
from core.dashboard_read.snapshot import ComplianceState


def test_compliance_state(monkeypatch):
    class DummyComplianceMetrics:
        audit_packs_generated = 12
        last_audit_timestamp = "2026-02-02T12:00:00Z"
        violations_detected = 0
        regulator_exports_ready = True

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.compliance.read_compliance_metrics",
        lambda: DummyComplianceMetrics(),
    )

    state = build_compliance_state()

    assert isinstance(state, ComplianceState)
    assert state.audit_packs_ready is True
    assert state.regulator_ready is True
