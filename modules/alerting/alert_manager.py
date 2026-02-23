from datetime import datetime
from .models import AlertEvent


class AlertManager:
    def __init__(self, channels):
        self._channels = channels

    def emit(self, *, severity, category, message, context):
        alert = AlertEvent(
            timestamp=datetime.utcnow(),
            severity=severity,
            category=category,
            message=message,
            context=context,
        )

        for ch in self._channels:
            try:
                ch.send(alert)
            except Exception:
                pass  # alerts must never crash system
