# modules/operator_dashboard/adapters/alerts_adapter.py

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AlertSnapshot:
    """
    Read-only dashboard alert view.

    Alerts are OPTIONAL in the system.
    This adapter must NEVER assume a concrete backend exists.
    """

    level: str
    message: str


def get_alerts_snapshot() -> List[AlertSnapshot]:
    """
    Return recent operator alerts for dashboard display.

    Safe behavior:
    - If no alert backend exists → return empty list
    """

    try:
        # Optional import — may not exist in minimal deployments
        from core.live_trading.alerts import get_recent_alerts
    except Exception:
        return []

    try:
        alerts = get_recent_alerts()
    except Exception:
        return []

    snapshots: List[AlertSnapshot] = []

    for alert in alerts:
        snapshots.append(
            AlertSnapshot(
                level=getattr(alert, "level", "INFO"),
                message=getattr(alert, "message", str(alert)),
            )
        )

    return snapshots
