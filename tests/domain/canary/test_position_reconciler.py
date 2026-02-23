from datetime import datetime
from domain.canary.position_reconciler import PositionReconciler
from domain.canary.system_position_record import SystemPositionRecord
from domain.broker.broker_position_snapshot import BrokerPositionSnapshot


def test_position_reconciliation_detects_mismatch():
    sys = SystemPositionRecord("NIFTY", 1, 19500)

    broker = BrokerPositionSnapshot(
        symbol="NIFTY",
        quantity=2,
        average_price=19500,
        market_value=39000,
        as_of=datetime.utcnow(),
    )

    res = PositionReconciler.reconcile(sys, broker)
    assert res.matched is False
