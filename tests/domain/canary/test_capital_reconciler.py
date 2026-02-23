from datetime import datetime
from domain.canary.capital_reconciler import CapitalReconciler
from domain.canary.authorized_trade_record import AuthorizedTradeRecord
from domain.broker.broker_trade_snapshot import BrokerTradeSnapshot


def test_reconciliation_within_tolerance():
    auth = AuthorizedTradeRecord("I1", "NIFTY", "BUY", 10000)

    broker = BrokerTradeSnapshot(
        order_id="O1",
        symbol="NIFTY",
        side="BUY",
        executed_qty=1,
        executed_price=10050,
        executed_value=10050,
        executed_at=datetime.utcnow(),
    )

    res = CapitalReconciler.reconcile(auth, broker, tolerance_pct=0.01)
    assert res.within_tolerance is True
