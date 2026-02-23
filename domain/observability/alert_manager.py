from typing import List
from domain.observability.alert import Alert


class AlertManager:
    """
    Stores alerts. Does NOT act on them.
    """

    def __init__(self):
        self._alerts: List[Alert] = []

    def raise_alert(self, alert: Alert) -> None:
        self._alerts.append(alert)

    def active(self) -> List[Alert]:
        return list(self._alerts)
