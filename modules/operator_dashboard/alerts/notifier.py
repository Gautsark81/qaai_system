from typing import Iterable

from operator_dashboard.alerts.alert_event import AlertEvent
from operator_dashboard.observability.event_bus import EventBus


def notify(alerts: Iterable[AlertEvent]) -> None:
    """
    Push alerts into observability pipeline.
    """
    bus = EventBus()

    for alert in alerts:
        bus.emit(alert)
