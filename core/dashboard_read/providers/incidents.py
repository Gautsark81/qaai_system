from core.dashboard_read.snapshot import IncidentState
from core.dashboard_read.providers._sources import incidents as incident_source


def build_incident_state() -> IncidentState:
    """
    Read-only incident state provider.
    Copy-only.
    No escalation logic.
    """

    metrics = incident_source.read_incident_metrics()

    return IncidentState(
        open_incidents=metrics.open_incidents,
        total_incidents=metrics.total_incidents,
        last_incident_type=metrics.last_incident_type,
        capital_frozen=metrics.capital_frozen,
    )
