from datetime import datetime
from domain.canary.reconciliation_alert_emitter import ReconciliationAlertEmitter
from domain.canary.reconciliation_result import ReconciliationResult
from domain.observability.alert_manager import AlertManager


def test_alert_emitted_on_drift():
    mgr = AlertManager()

    res = ReconciliationResult(
        intent_id="I1",
        authorized_capital=10000,
        broker_executed_capital=10500,
        delta=500,
        within_tolerance=False,
    )

    ReconciliationAlertEmitter.emit(res, mgr)
    assert len(mgr.active()) == 1
