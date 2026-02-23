from core.dashboard_read.snapshot import ComplianceState
from core.dashboard_read.providers._sources import compliance as compliance_source


def build_compliance_state() -> ComplianceState:
    """
    Read-only compliance state provider.
    Copy-only.
    """

    metrics = compliance_source.read_compliance_metrics()

    return ComplianceState(
        audit_packs_ready=metrics.audit_packs_generated > 0,
        last_bundle_hash=metrics.last_audit_timestamp,
        notarized=True,
        regulator_ready=metrics.regulator_exports_ready,
    )
