from domain.canary.position_alert_emitter import PositionAlertEmitter
from domain.canary.position_reconciliation_result import (
    PositionReconciliationResult
)
from domain.observability.alert_manager import AlertManager


def test_position_alert_emitted():
    mgr = AlertManager()

    res = PositionReconciliationResult(
        symbol="NIFTY",
        system_qty=1,
        broker_qty=2,
        delta_qty=1,
        matched=False,
    )

    PositionAlertEmitter.emit(res, mgr)
    assert len(mgr.active()) == 1
