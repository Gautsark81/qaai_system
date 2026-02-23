from core.dashboard.snapshot import CoreSystemSnapshot
from dashboard.view_models import AlertsVM


def alerts_adapter(snapshot: CoreSystemSnapshot) -> AlertsVM:
    """
    Phase-9.2 adapter:
    Alerts are rendered, never interpreted.
    """

    alerts = tuple(snapshot.alerts)

    return AlertsVM(
        count=len(alerts),
        alerts=alerts,
    )
