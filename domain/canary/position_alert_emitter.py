from datetime import datetime
from domain.canary.position_reconciliation_result import (
    PositionReconciliationResult
)
from domain.canary.position_alert_policy import PositionAlertPolicy
from domain.observability.alert import Alert
from domain.observability.alert_manager import AlertManager


class PositionAlertEmitter:
    """
    Emits alerts on holdings mismatch.
    """

    @staticmethod
    def emit(
        result: PositionReconciliationResult,
        alert_manager: AlertManager,
    ) -> None:

        if not PositionAlertPolicy.should_alert(result.matched):
            return

        alert_manager.raise_alert(
            Alert(
                severity="CRITICAL",
                source="POSITION_RECONCILIATION",
                message=(
                    f"Position mismatch for {result.symbol}: "
                    f"system_qty={result.system_qty}, "
                    f"broker_qty={result.broker_qty}"
                ),
                created_at=datetime.utcnow(),
            )
        )
