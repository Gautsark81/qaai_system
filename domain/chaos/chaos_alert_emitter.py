from datetime import datetime
from domain.chaos.chaos_impact import ChaosImpact
from domain.observability.alert import Alert
from domain.observability.alert_manager import AlertManager


class ChaosAlertEmitter:
    """
    Emits alerts when chaos impacts trading.
    """

    @staticmethod
    def emit(
        impact: ChaosImpact,
        source: str,
        alert_manager: AlertManager,
    ) -> None:

        if not impact.should_halt_trading:
            return

        alert_manager.raise_alert(
            Alert(
                severity=impact.severity,
                source=source,
                message="Chaos condition detected — trading halted",
                created_at=datetime.utcnow(),
            )
        )
