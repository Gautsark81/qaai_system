# providers/risk.py
from core.dashboard_read.snapshot import RiskState
from core.dashboard_read.providers._sources import risk as risk_source

def build_risk_state() -> RiskState:
    m = risk_source.read_risk_metrics()
    return RiskState(
        checks_passed=m.checks_passed,
        checks_failed=m.checks_failed,
        dominant_violation=m.dominant_violation,
        freeze_active=m.freeze_active,
    )
