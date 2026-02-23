from datetime import datetime
from domain.canary.reconciliation_result import ReconciliationResult
from domain.observability.alert import Alert
from domain.observability.alert_manager import AlertManager
from domain.canary.reconciliation_alert_policy import ReconciliationAlertPolicy


class ReconciliationAlertEmitter:
    """
    Emits alerts for capital drift.
    """

    @staticmethod
    def emit(
        result: ReconciliationResult,
        alert_manager: AlertManager,
    ) -> None:

        if not ReconciliationAlertPolicy.should_alert(
            result.within_tolerance
        ):
            return

        alert_manager.raise_alert(
            Alert(
                severity="HIGH",
                source="CAPITAL_RECONCILIATION",
                message=(
                    f"₹ drift detected: intent={result.intent_id}, "
                    f"authorized={result.authorized_capital}, "
                    f"executed={result.broker_executed_capital}, "
                    f"delta={result.delta}"
                ),
                created_at=datetime.utcnow(),
            )
        )
